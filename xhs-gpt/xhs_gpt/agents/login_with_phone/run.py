import tempfile
from time import sleep
from typing import Optional

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from playwright.sync_api import sync_playwright

from xhs import XhsClient, DataFetchError
from xhs_gpt.utils import unzip_prompt_run, STEALTH_JS


def sign(uri, data=None, a1="", web_session=""):
    for _ in range(10):
        try:
            with sync_playwright() as playwright:
                stealth_js_path = STEALTH_JS
                chromium = playwright.chromium

                # 如果一直失败可尝试设置成 False 让其打开浏览器，适当添加 sleep 可查看浏览器状态
                browser = chromium.launch(headless=True)

                browser_context = browser.new_context()
                browser_context.add_init_script(path=stealth_js_path)
                context_page = browser_context.new_page()
                context_page.goto("https://www.xiaohongshu.com")
                browser_context.add_cookies([{'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"}])
                context_page.reload()
                # 这个地方设置完浏览器 cookie 之后，如果这儿不 sleep 一下签名获取就失败了，如果经常失败请设置长一点试试
                sleep(1)
                encrypt_params = context_page.evaluate("([url, data]) => window._webmsxyw(url, data)", [uri, data])
                return {"x-s": encrypt_params["X-s"], "x-t": str(encrypt_params["X-t"])}
        except Exception as e:
            print(e)
            # 这儿有时会出现 window._webmsxyw is not a function 或未知跳转错误，因此加一个失败重试趴
            pass
    raise Exception("重试了这么多次还是无法签名成功，寄寄寄")


class GetUserPhoneNumber:
    tool = {"name": "get_user_phone_number",
            "description": "Get user phone number to login to Xiaohongshu account. Response with the phone number.",
            "parameters": {"type": "object", "properties": {}}}

    @classmethod
    def run(cls, ):
        phone_number = input("Please provide your phone number >>>")
        xhs_client = XhsClient(sign=sign)
        return {"phone_number": phone_number}

        return {"phone_number": phone_number,
                "status": 'verification code sent successfully, now ask for verification code'}


class SendVerificationCode:
    tool = {"name": "send_verification_code",
            "description": "Send verification code to user phone. Response with `token_file`.",
            "parameters": {"type": "object", "properties": {"phone_number": {"type": "string", }, },
                           "required": ["phone_number"]}}

    @classmethod
    def run(cls, phone_number):
        xhs_client = XhsClient(sign=sign)
        try:
            res = xhs_client.send_code(phone_number)
        except DataFetchError as e:
            return {"status": 'verification code sent failed', "reason": str(e)}
        retry = 3
        token = None
        for i in range(retry):
            try:
                verification_code = input("Please provide the verification code >>>")
                check_res = xhs_client.check_code(phone_number, verification_code)
                print(check_res)
                token = check_res["mobile_token"]
                break
            except DataFetchError as e:
                print(e)
                print('Remaining retry times: ', retry - i - 1)
        if token is None:
            return {"status": 'verification code check failed, please check phone number', }
        login_res = xhs_client.login_code(phone_number, token)
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.cookie', prefix='xhs_login_') as f:
            f.write(xhs_client.cookie)
        return {'status': login_res, 'token_file': f.name}


tool_prompts, tool_runs = unzip_prompt_run([GetUserPhoneNumber, SendVerificationCode, ])
prompt = ChatPromptTemplate.from_messages([("system", """You are helping user to get the `token_file` which contains tokens to login to Xiaohongshu.
Generally, you need to first get user's phone number, then send verification code.
Provide user friendly feedback.
Always use a tool!"""), ("user", "{input}"), MessagesPlaceholder(variable_name="agent_scratchpad"), ])

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106")
llm_with_tools = llm.bind(functions=tool_prompts)
login_with_phone_agent = ({"input": lambda x: x["input"], "agent_scratchpad": lambda x: format_to_openai_functions(
    x["intermediate_steps"]), } | prompt | llm_with_tools | OpenAIFunctionsAgentOutputParser())

from langchain.pydantic_v1 import BaseModel


class LoginWithPhoneInput(BaseModel):
    input: Optional[str] = """Let's start"""


class LoginWithPhoneOutput(BaseModel):
    output: str


login_with_phone_agent_executor = AgentExecutor(agent=login_with_phone_agent, tools=tool_runs, max_iterations=15,
                                                early_stopping_method="generate",
                                                return_intermediate_steps=True, verbose=True).with_types(
    input_type=LoginWithPhoneInput, output_type=LoginWithPhoneOutput)


class LoginWithPhone:
    tool = {"name": "login_with_phone",
            "description": "Login to Xiaohongshu with phone. Response with `token_file` which contains login token.",
            "parameters": {"type": "object", "properties": {}, }}

    @classmethod
    def run(cls):
        result = login_with_phone_agent_executor.invoke({'input': """Let's start"""})
        print(result['output'])
        return result['intermediate_steps'][-1][1]


if __name__ == '__main__':
    result = login_with_phone_agent_executor.invoke({'input': """Let's start"""})
    print(result)
