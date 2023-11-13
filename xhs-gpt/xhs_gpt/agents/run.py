from langchain.agents.agent import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from xhs_gpt.agents.create_note.run import CreateNote
from xhs_gpt.agents.get_feed.run import GetFeed
from xhs_gpt.agents.get_note.run import GetNote
from xhs_gpt.agents.login_with_qrcode import LoginWithQRCode
# from xhs_gpt.agents.login_with_phone import LoginWithPhone
from xhs_gpt.utils import unzip_prompt_run

xhs_tool_prompts, xhs_tool_runs = unzip_prompt_run([
    # LoginWithPhone, # Login with phone requires entering phone number in console, not convenient
    LoginWithQRCode,  # Login with QR code will pop up an image window, easy to interact
    CreateNote,
    GetFeed,
    GetNote,
])

xhs_agent_prompt = ChatPromptTemplate.from_messages([("system", """You are a Xiaohongshu Assistant. Fulfill user requirements using given tools.
Pay attention the dependency relation among them, some tools may require the output of others."""), ("user", "{input}"),
                                                     MessagesPlaceholder(variable_name="agent_scratchpad"), ])

llm = ChatOpenAI(temperature=.3, model="gpt-4-1106-preview")
xhs_llm = llm.bind(functions=xhs_tool_prompts)
from langchain.pydantic_v1 import BaseModel, Field


class XHSInput(BaseModel):
    input: str = Field(description="What's your plan with Xiaohongshu?",
                       default='分析情感领域中最受欢迎的一篇笔记，针对其内容发表一篇犀利风趣的笔记。我偏好通过二维码登录。')


class XHSOutput(BaseModel):
    output: str


xhs_agent = ({"input": lambda x: x["input"], "agent_scratchpad": lambda x: format_to_openai_functions(
    x["intermediate_steps"]), } | xhs_agent_prompt | xhs_llm | OpenAIFunctionsAgentOutputParser())

xhs_agent_executor = AgentExecutor(agent=xhs_agent, tools=xhs_tool_runs, max_iterations=15,
                                   early_stopping_method="generate", return_intermediate_steps=True,
                                   verbose=True).with_types(input_type=XHSInput, output_type=XHSOutput)

if __name__ == '__main__':
    result = xhs_agent_executor.invoke(
        {'input': '分析情感领域中最受欢迎的一篇笔记，针对其内容发表一篇犀利风趣的笔记。我偏好通过二维码登录。'})
    print(result['output'])
