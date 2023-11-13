import datetime
import json
import logging
import tempfile
from operator import itemgetter
from typing import Optional

import requests
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.pydantic_v1 import BaseModel
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnableLambda

from xhs import XhsClient
from xhs_gpt.utils import unzip_prompt_run

json_llm = ChatOpenAI(temperature=.7, model="gpt-4-1106-preview").bind(response_format={"type": "json_object"})
create_note_body_prompt = ChatPromptTemplate.from_messages([
    ('system', """User will provide you with an basic idea, and you are helping user to generate an attractive Xiaohongshu post in JSON. A post contains a title, a description and a list of tags. Include line break in description.
    
Use the following writing styles:

1. Friendly and Casual: Posts on Xiaohongshu are typically written in the first person, creating a feeling of sharing between friends. The language is colloquial and down-to-earth, making it approachable and relatable.

2. Rich in Visual Content: Xiaohongshu posts often come with numerous pictures, which are closely integrated with the text content, making the information more intuitive and understandable.

3. Use of Emoji: Xiaohongshu posts frequently use emojis to enrich expression and add fun, making the content more lively and engaging.

4. High Interactivity: Xiaohongshu posts usually encourage readers to participate in discussions, for example by asking questions or initiating topics, enhancing the interactivity of the posts.

5. Practicality: Xiaohongshu posts often provide practical information, such as product use experiences, travel strategies, etc. These pieces of information are based on personal actual experiences and have high reference value.

# Xiaohongshu JSON post Examples
{{"title": "绝了❗️为“哄”孩子喝光牛奶，设计师有妙招👏", 
"description": "近年来，日本学校午餐牛奶剩余问题已成为小学和初中难以解决的问题。因此。奥美日本为Seki Milk重新设计了包装：将漫画用白色的笔印刻在瓶身之上，若想看完漫画内容，就必须把整瓶牛奶干光！\n这是一个独特的想法，并得到了很多回应。牛奶瓶上画的是漫画家阿美明彦的原创作品《牛奶怪物》，总共多达10集。\n该牛奶在岐阜县关市旭丘小学的学校午餐时间试用时，孩子们的反应都非常好，有些小朋友说：“漫画很有趣，学校的午餐也变得有趣！”", 
"tags": ["工业设计", "设计灵感", "产品设计", "漫画", "设计", "牛奶", "牛奶瓶", "包装设计"] }}
{{"title": "158/102 来看小狗流鼻涕", 
"description": "衣服上的狗狗太可爱了💧", 
"tags": ["今天穿什么香", "狗狗t", "白短裤", "小个子穿搭"]}}
{{"title": "这种又粘人又帅的混血帅哥到底是谁在谈啊", 
"description": "原来是我自己", 
"tags": ["姐弟恋", "异国恋", "混血", "小奶狗", "外国男友", "男朋友", "恋爱", "恋爱日常", "甜甜的恋爱", "情侣", "小情侣的日常", "日常碎片PLOG", "笔记灵感"]}}
{{"title": "🍁来Arrow Town赏秋", 
"description": "深秋的箭镇好治愈，漫山遍野的秋色，仿佛打翻了颜料盘🎨，来了箭镇要好好拍照记录📝。\n\n📷拍照点：1⃣️Wilcox Green：Wilcox Green是个拍照标志地，最佳拍照时间在下午四点左右，但是容易发生在你拍照的时候，旁边等着很多游客，这时候只能尴尬地笑笑，表情管理有点难😅\n2⃣️箭镇大草坪：Wilcox Green所在的大草坪，选一处人少的地方拍照片，这时候怎么凹造型都没人催\n3⃣️街景：在箭镇，拍拍Buckingham Street和Arrow Lane的街景和建筑也不错，可多走两步到Wiltshire Street找个高点往下拍五彩树林和街景\nps：找到一段在施工的路，我在保证安全的前提下坐在地上拍了一张，但不推荐。\n\n箭镇每年赏秋最佳季节是四月中旬到五月初，四月最后一周会举办金秋节，这个季节这边时有阵雨🌦️，但是阴雨天的箭镇也有不一样的感觉，这次在箭镇我全程用富士相机📷，适配指数💯", 
"tags": ["五一去哪玩", "新西兰", "新西兰箭镇", "和大自然亲密接触", "治愈系风景", "富士相机"]}}
{{"title": "五一出游好去处｜洞头岛屿生活市集", 
"description": "刚从南京回来\n陪我回来的闺蜜问我去哪里玩\n这不赶巧了\n洞头刚好有台湾美食节！\n不只是美食\n还有精彩的舞台演出！\n\n网红打卡大黄鸭\n台湾美食一条gai\n免费啤酒畅饮\n精彩的乐队演出\n氛围感落日灯……\n真的又好出片\n又快乐……\n\n🕒4.29～5.3 17:00～21:00\n📍洞头北岙街道东沙渔港", 
"tags": ["温州探店", "洞头旅游攻略", "洞头旅游", "五一去哪儿"]}}"""),
    ('human', "{input}"),
])

create_note_body_chain = {'input': itemgetter(
    'topic')} | create_note_body_prompt | json_llm | StrOutputParser() | RunnableLambda(json.loads)


def create_image(size, style, prompt):
    import openai
    try:
        response = openai.images.generate(
            prompt=prompt,
            model='dall-e-3',
            n=1,
            size=size,
            style=style,
            quality='hd' if style == 'natural' else 'standard',
        )
        print(response.data[0].revised_prompt)
        return response.data[0].url
    except Exception as e:
        logging.exception(e)
        return None


class CreateImage:
    tool = {
        "name": "create_images",
        "description": "create images by English descriptions",
        "parameters": {
            "type": "object",
            "properties": {
                "size": {
                    "type": "string",
                    "description": "size of images, squared, wide or high",
                    "enum": ["1024x1024", "1792x1024", "1024x1792"]
                },
                "style": {
                    "type": "string",
                    "description": "style of images, natural means realistic while vivid means hyper-realistic",
                    "enum": ["natural", "vivid"]
                },
                "image_descriptions": {
                    "type": "array",
                    "description": "an array of English detailed descriptions of each images",
                    "items": {
                        "type": "string",
                        "description": "English description of one image"
                    }
                }
            },
            "required": ["size", "style", "image_descriptions"]
        }
    }

    @classmethod
    def run(cls, size, style, image_descriptions):
        print(size)
        print(style)
        print(image_descriptions)
        run = RunnableLambda(lambda x: create_image(size=size, style=style, prompt=x['prompt']))
        result = run.batch([{'prompt': i} for i in image_descriptions])
        return [i for i in result if i]


from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents.agent import AgentExecutor
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

create_image_tool_prompts = [i.tool for i in (
    CreateImage,
)]
create_image_tool_runs = [Tool.from_function(func=i.run, name=i.tool['name'], description=i.tool['description']) for i
                          in (
                              CreateImage,
                          )]

create_image_agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """User will show you a note on Xiaohongshu. You are helping user to generate rich and appropriate images which will be embeded into the note.
You need to first decide the number of images to generate, then their size and style. Each description maps to one image.
All images should have same size and style, but the descriptions of each images are different.
You need to derive the descriptions in your own words. They should be as detailed as possible.

# Example Image Descriptions
```
["A photorealistic depiction captures the essence of a playful Border Collie gracefully leaping over dandelions, with its tongue out and mischievous eyes sparkling. The contrast between its black and white coat against the vibrant green fields creates a impressive scene that is impossible to ignore.",
"Transport yourself into a cinematic experience with a mouthwatering dish presented on a pristine white plate, expertly arranged to create a visually stunning presentation. The vibrant colors and tantalizing aroma entice the senses, making it feel like a scene from a food-centric movie.",
"Step into a world of enchantment with a stunning makeup look flawlessly applied, enhancing the wearer's natural beauty with precision and artistry. The carefully chosen colors accentuate their eyes, lips, and cheekbones, creating an ethereal glow that exudes an air of confidence and elegance."]
```

Always response in English, and always generate more than 2 images."""),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

llm = ChatOpenAI(temperature=.5, model="gpt-3.5-turbo-1106").bind(function_call={"name": "create_images"})
create_image_llm = llm.bind(functions=create_image_tool_prompts)
create_image_agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_functions(
                x["intermediate_steps"]
            ),
        }
        | create_image_agent_prompt
        | create_image_llm
        | OpenAIFunctionsAgentOutputParser()
)

create_image_agent_executor = AgentExecutor(
    agent=create_image_agent, tools=create_image_tool_runs, max_iterations=1, early_stopping_method="force",
    return_intermediate_steps=True,
    verbose=True
)


class CreateNote:
    tool = {
        "name": "create_note",
        "description": "Create a note on Xiaohongshu. Require login.",
        "parameters": {"type": "object",
                       "properties": {
                           "description": {
                               "type": "string",
                               "description": "detailed description of this note"
                           },
                           "token_file": {
                               "type": "string",
                               "description": "generated by `login` tool"
                           },
                       },
                       'required': ['topic', 'token_file']
                       }
    }

    @classmethod
    def run(cls, topic, token_file):
        from xhs_gpt.utils import sign
        with open(token_file, 'r') as f:
            cookie = f.read()
        xhs_client = XhsClient(cookie=cookie, sign=sign)
        print(xhs_client.get_self_info())
        note = create_note_body_chain.invoke({'topic': topic})
        print(note)
        image_actions = create_image_agent_executor.invoke({'input': f"""{note['title']}\n\n{note['description']}"""})
        image_urls = image_actions['intermediate_steps'][-1][1]
        images = []
        for image_url in image_urls:
            with tempfile.NamedTemporaryFile('wb', delete=False) as f:
                f.write(requests.get(image_url).content)
                images.append(f.name)
        topics = []
        for t in note['tags']:
            try:
                topics.append(xhs_client.get_suggest_topic(t)[0])
            except:
                pass
        topic_descriptions = [f'''#{i["name"]}[话题]#''' for i in topics]
        note['description'] += '\n' + ' '.join(topic_descriptions)
        note = xhs_client.create_image_note(note['title'], note['description'], images, is_private=False, topics=topics,
                                            post_time=datetime.datetime.now().__format__("%Y-%m-%d %H:%M:%S"))
        return note


create_note_tool_prompts, create_note_tool_runs = unzip_prompt_run([
    CreateNote,
])

create_note_agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         """You are a Xiaohongshu Assistant. Help user to refine their topic, then create a note. token_file: {token_file}"""),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

llm = ChatOpenAI(temperature=.5, model="gpt-3.5-turbo-1106")
create_note_llm = llm.bind(functions=create_note_tool_prompts)


class CreateNoteInput(BaseModel):
    description: str
    token_file: Optional[str | None] = None


class CreateNoteOutput(BaseModel):
    output: str


create_note_agent = (
        {
            "description": lambda x: x["description"],
            "token_file": lambda x: x["token_file"] if 'token_file' in x else None,
            "agent_scratchpad": lambda x: format_to_openai_functions(
                x["intermediate_steps"]
            ),
        }
        | create_note_agent_prompt
        | create_note_llm
        | OpenAIFunctionsAgentOutputParser()
)

create_note_agent_executor = AgentExecutor(
    agent=create_note_agent, tools=create_note_tool_runs, max_iterations=3, early_stopping_method="generate",
    return_intermediate_steps=True,
    verbose=True
).with_types(input_type=CreateNoteInput, output_type=CreateNoteOutput)

if __name__ == '__main__':
    print(create_note_agent_executor.invoke(
        {'description': '狗狗萌宠', 'token_file': '/tmp/xhs_login.cookie'}))  # replace with your token_file
