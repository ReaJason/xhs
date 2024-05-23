import asyncio
import configparser
import json
import logging
import os.path
import random
import re
import time

from apscheduler.schedulers.blocking import BlockingScheduler
from playwright.async_api import Playwright, async_playwright

con = configparser.ConfigParser()

# 读取文件
con.read("./config.ini", encoding='utf-8')
class ConfigUtils:
    @staticmethod
    def get(key:str, section='default'):
        items = con.items(section) 	# 返回结果为元组
        items = dict(items)
        return items.get(key)
    @staticmethod
    def set(key:str, value:str, section='default'):
        con.set(section, key, value )
        with open("./config.ini", 'w', encoding="utf-8") as configfile:
            con.write(configfile)

video_path = ConfigUtils.get("video_path")
headless = ConfigUtils.get("headless").__eq__("否")
def find_file(find_path, file_type) -> list:
    """
    寻找文件
    :param find_path: 子路径
    :param file_type: 文件类型
    :return:
    """
    path = os.path.join(os.path.abspath(""), find_path)
    if not os.path.exists(path):
        os.makedirs(path)
    data_list = []
    for root, dirs, files in os.walk(path):
        if root != path:
            break
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.find(file_type) != -1:
                data_list.append(file_path)
    return data_list

def check_in(cookie_name, number):

    with open(f"temp/issue.json", "r") as file:
        json_data = json.load(file)
    data = json_data.get(cookie_name)
    if data is None:
        return False
    return number in data

def add_issue_id(cookie_name, id):
    with open(f"temp/issue.json", "r") as file:
        json_data = json.load(file)
    if cookie_name in json_data:
        json_data[cookie_name].append(id)
    else:
        json_data[cookie_name] = [id]
    with open(f"temp/issue.json", "w") as file:
        json.dump(json_data, file)

class upload_douyin():

    async def playwright_init(self, p: Playwright):

        browser = await p.chromium.launch(headless=headless,
                                          chromium_sandbox=False,
                                          ignore_default_args=["--enable-automation"],
                                          channel="chrome"
                                          )
        return browser

    def __init__(self, timeout: int, cookie_file: str):
        self.title = ""
        self.ids = ""
        self.video_path = ""
        self.video_ids = []
        self.page = 0
        self.path = os.path.abspath('')
        self.ua = {
            "web": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 "
                   "Safari/537.36",
            "app": "com.ss.android.ugc.aweme/110101 (Linux; U; Android 5.1.1; zh_CN; MI 9; Build/NMF26X; "
                   "Cronet/TTNetVersion:b4d74d15 2020-04-23 QuicVersion:0144d358 2020-03-24)"
        }
        self.timeout = timeout * 1000
        self.cookie_file = cookie_file

    async def upload(self, p: Playwright) -> None:
        browser = await self.playwright_init(p)
        context = await browser.new_context(storage_state=self.cookie_file, user_agent=self.ua["web"])
        page = await context.new_page()
        await page.add_init_script(path="stealth.min.js")
        await page.goto("https://creator.douyin.com/creator-micro/content/upload")
        print("正在判断账号是否登录")
        if "/creator-micro/" not in page.url:
            print("账号未登录")
            logging.info("账号未登录")
            return
        print("账号已登录")
        try:
            话题个数 = 1;
            话题 = ["大学生日常", "vlog", "周末时光"]
            emoji_list = ["😀","😁","😂","🤣","😄","😅","😆","😎"]
            video_desc = ""
            for i in range(0, 话题个数):
                video_desc = video_desc + f"#{话题[random.randint(0, len(话题) - 1)]} "
            video_desc = video_desc + self.video_path.split("\\")[-1].replace(".mp4", "") + emoji_list[random.randint(0, len(emoji_list) - 1)]

            try:
                async with page.expect_file_chooser() as fc_info:
                    await page.locator(
                        "label:has-text(\"点击上传 或直接将视频文件拖入此区域为了更好的观看体验和平台安全，平台将对上传的视频预审。超过40秒的视频建议上传横版视频\")").click()
                file_chooser = await fc_info.value
                await file_chooser.set_files(self.video_path, timeout=self.timeout)
            except Exception as e:
                print("发布视频失败，可能网页加载失败了\n", e)
                logging.info("发布视频失败，可能网页加载失败了")

            try:
                await page.locator(".modal-button--38CAD").click()
            except Exception as e:
                print(e)
            await page.wait_for_url(
                "https://creator.douyin.com/creator-micro/content/publish?enter_from=publish_page")
            # css视频标题选择器
            css_selector = ".zone-container"
            await page.locator(".ace-line > div").click()

            await page.type(css_selector, video_desc)
            await page.press(css_selector, "Space")
            print("视频标题输入完毕，等待发布")
            # await page.get_by_text("请选择合集").click()
            # await page.locator("div").filter(has_text=re.compile(r"^大学生日常$")).click()

            is_while = False
            while True:
                # 循环获取点击按钮消息
                time.sleep(2)
                try:
                    await page.get_by_role("button", name="发布", exact=True).click()
                    try:
                        print(video_desc)
                        await page.wait_for_url("https://creator.douyin.com/creator-micro/content/manage")
                        logging.info("账号发布视频成功")
                        print("账号发布视频成功")
                        break
                    except Exception as e:
                        print(e)
                except Exception as e:
                    print(e)
                    break
                msg = await page.locator('//*[@class="semi-toast-content-text"]').all_text_contents()
                for msg_txt in msg:
                    print("来自网页的实时消息：" + msg_txt)
                    if msg_txt.find("发布成功") != -1:
                        is_while = True
                        logging.info("账号发布视频成功")
                        print("账号发布视频成功")
                    elif msg_txt.find("上传成功") != -1:
                        try:
                            await page.locator('button.button--1SZwR:nth-child(1)').click()
                        except Exception as e:
                            print(e)
                            break
                        msg2 = await page.locator(
                            '//*[@class="semi-toast-content-text"]').all_text_contents()
                        for msg2_txt in msg2:
                            if msg2_txt.find("发布成功") != -1:
                                is_while = True
                                logging.info("账号发布视频成功")
                                print("账号发布视频成功")
                            elif msg2_txt.find("已封禁") != -1:
                                is_while = True
                                logging.info("账号视频发布功能已被封禁")
                                print("账号视频发布功能已被封禁")
                    elif msg_txt.find("已封禁") != -1:
                        is_while = True
                        print("视频发布功能已被封禁")
                        logging.info("视频发布功能已被封禁")
                    else:
                        pass

                    if is_while:
                        break



        except Exception as e:
            print("发布视频失败，cookie已失效，请登录后再试\n", e)
            logging.info("发布视频失败，cookie已失效，请登录后再试")
    async def main(self, cookie_name):
        async with async_playwright() as playwright:
            file_list = os.listdir(video_path)
            for file_name in file_list:
                file_path = os.path.join(video_path, file_name)
                # 判断是否为文件
                if os.path.isfile(file_path):
                    p,f = os.path.split(file_path)
                    if f.endswith("mp4") or f.endswith("mov"):
                        if check_in(cookie_name, f.split('.')[0]):
                            continue
                        self.video_path = file_path
                        await self.upload(playwright)
                        add_issue_id(cookie_name, f.split('.')[0])
                        break;
def run():
    cookie_list = find_file("cookie", "json")
    x = 0
    for cookie_path in cookie_list:
        x += 1
        cookie_name: str = os.path.basename(cookie_path)
        print("正在使用[%s]发布作品，当前账号排序[%s]" % (cookie_name, str(x)))
        app = upload_douyin(60, cookie_path)
        asyncio.run(app.main(cookie_name))
        print("发送成功")
if __name__ == '__main__':
    minutes= ConfigUtils.get("minutes")
    run()
    scheduler = BlockingScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(run, 'interval', minutes=int(minutes), misfire_grace_time=900)
    scheduler.start()
