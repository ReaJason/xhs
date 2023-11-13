import datetime
import json
import tempfile
import tkinter as tk
from time import sleep
from typing import Optional

import qrcode
from PIL import Image, ImageTk
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from playwright.sync_api import sync_playwright

from xhs import XhsClient


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
                browser_context.add_cookies([
                    {'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"}]
                )
                context_page.reload()
                # 这个地方设置完浏览器 cookie 之后，如果这儿不 sleep 一下签名获取就失败了，如果经常失败请设置长一点试试
                sleep(1)
                encrypt_params = context_page.evaluate("([url, data]) => window._webmsxyw(url, data)", [uri, data])
                return {
                    "x-s": encrypt_params["X-s"],
                    "x-t": str(encrypt_params["X-t"])
                }
        except Exception as e:
            print(e)
            # 这儿有时会出现 window._webmsxyw is not a function 或未知跳转错误，因此加一个失败重试趴
            pass
    raise Exception("重试了这么多次还是无法签名成功，寄寄寄")


class GenerateQRCode:
    tool = {
        "name": "generate_login_qrcode",
        "description": "Generate a qrcode for login. Response with the string path to the qrcode image, the `qr_id` and `qr_code`.",
        "parameters": {"type": "object",
                       "properties": {
                       }
                       }
    }

    @classmethod
    def run(cls, ):
        # print(prompt)
        xhs_client = XhsClient(sign=sign)
        print(datetime.datetime.now())
        qr_res = xhs_client.get_qrcode()
        qr_id = qr_res["qr_id"]
        qr_code = qr_res["code"]
        qr = qrcode.QRCode(version=1, error_correction=qrcode.ERROR_CORRECT_L,
                           box_size=50,
                           border=1)
        qr.add_data(qr_res["url"])
        qr.make()
        img = qr.make_image()
        new_size = (300, 300)  # New size for the QR code image
        img = img.resize(new_size)
        with tempfile.NamedTemporaryFile('wb', delete=False, suffix='.jpg', prefix='xhs_login_') as f:
            img.save(f.name)
        return {
            'path': f.name,
            'qr_id': qr_id,
            'qr_code': qr_code,
        }


class DisplayQRCode:
    tool = {
        "name": "display_login_qrcode",
        "description": "Display the login QR code image to user.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    'description': 'path to qrcode'
                },
            },
            "required": ["path"]
        }
    }

    @classmethod
    def run(cls, path):
        def close_window():
            root.destroy()

        # 创建GUI窗口
        root = tk.Tk()

        # 打开图片
        image_path = path
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)

        # 显示图片
        label = tk.Label(root, image=photo)
        label.pack()

        # 显示文字
        text = """Scan the QR Code, confirm login on your phone, then close the window to continue.
扫描二维码，在手机上确认登录，然后关闭该窗口。"""
        text_label = tk.Label(root, text=text, font=("song ti", 16))
        text_label.pack()

        # 监听窗口关闭事件
        root.protocol("WM_DELETE_WINDOW", close_window)

        # 运行GUI窗口
        root.mainloop()
        print('QR code closed')
        return 'QR code scanned. Now check status.'


class CheckQRCode:
    tool = {
        "name": "check_login_qrcode",
        "description": "Verify the login status. Response with the `login_status` and `token_file`.",
        "parameters": {
            "type": "object",
            "properties": {
                "qr_id": {
                    "type": "string",
                },
                "qr_code": {
                    "type": "string",
                }
            },
            "required": ["qr_id", "qr_code"]
        }
    }

    @classmethod
    def run(cls, qr_id, qr_code):
        xhs_client = XhsClient(sign=sign)
        for _ in range(3):
            check_qrcode = xhs_client.check_qrcode(qr_id, qr_code)
            print(check_qrcode)
            sleep(1)
            if check_qrcode["code_status"] == 2:
                print(json.dumps(check_qrcode["login_info"], indent=4))
                with tempfile.NamedTemporaryFile('w', delete=False, suffix='.cookie', prefix='xhs_login_') as f:
                    f.write(xhs_client.cookie)
                return {
                    'login_status': 'success',
                    'token_file': f.name,
                }
        return {
            'login_status': 'fail to login, did you really scan the qr code before closing it?',
            'token_file': None
        }


from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents.agent import AgentExecutor
from xhs_gpt.utils import unzip_prompt_run, STEALTH_JS

tool_prompts, tool_runs = unzip_prompt_run([
    GenerateQRCode,
    DisplayQRCode,
    CheckQRCode,
])

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """You are helping user to get the `token_file` which contains tokens to login to Xiaohongshu.
Generally, you need to first generate a login QR code, then display the QR code to user for scanning, and finally check the QR code status to see whether login has succeeded.
Provide user friendly feedback.
Always use a tool!"""),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106")
llm_with_tools = llm.bind(functions=tool_prompts)
login_with_qrcode_agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_functions(
                x["intermediate_steps"]
            ),
        }
        | prompt
        | llm_with_tools
        | OpenAIFunctionsAgentOutputParser()
)

from langchain.pydantic_v1 import BaseModel


class LoginWithQRCodeInput(BaseModel):
    input: Optional[str] = """Let's start"""


class LoginWithQRCodeOutput(BaseModel):
    output: str


login_with_qrcode_agent_executor = AgentExecutor(
    agent=login_with_qrcode_agent, tools=tool_runs, max_iterations=15, early_stopping_method="generate",
    return_intermediate_steps=True,
    verbose=True
).with_types(input_type=LoginWithQRCodeInput, output_type=LoginWithQRCodeOutput)


class LoginWithQRCode:
    tool = {
        "name": "login_with_qrcode",
        "description": "Login to Xiaohongshu with QR code. Response with `token_file` which contains login token.",
        "parameters": {
            "type": "object",
            "properties": {
            },
        }
    }

    @classmethod
    def run(cls):
        result = login_with_qrcode_agent_executor.invoke({'input': """Let's start"""})
        print(result['output'])
        return result['intermediate_steps'][-1][1]


if __name__ == '__main__':
    result = login_with_qrcode_agent_executor.invoke({'input': """Let's start"""})
    print(result)
