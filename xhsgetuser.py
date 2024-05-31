import datetime
import os
import random
import sqlite3
import time
from time import sleep

import requests
from playwright.sync_api import sync_playwright
from sqlalchemy import update

from plus.core_plus import XhsClientPLUS
from plus.db_utils import DB_UTILS, SessionLocal
from plus.model.Model import Comment
from xhs import XhsClient, SearchSortType
import os
import random
import sqlite3
import time
from time import sleep

import requests
from playwright.sync_api import sync_playwright

from xhs import XhsClient, SearchSortType


def sign(uri, data=None, a1="", web_session=""):
    for _ in range(10):
        try:
            with sync_playwright() as playwright:
                stealth_js_path = r"./stealth.min.js"
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
        except Exception:
            # 这儿有时会出现 window._webmsxyw is not a function 或未知跳转错误，因此加一个失败重试趴
            pass
    raise Exception("重试了这么多次还是无法签名成功，寄寄寄")

class XhsCli():

    @staticmethod
    def get_client(token):
        return XhsClient(token, sign=sign)
# with open("./demoxy2.txt", "r", encoding="utf8") as f:
#     demo = f.read()

class XhsCli():
    @staticmethod
    def get_client():
        cookie = "acw_tc=3e6a957a21c386fe2b0422da4fd0acf542b2076f20cc0d1e04fa7908385be0f8; a1=18fc3260659yceywi7ojzg2nb1hxztup07pp5vbbo50000545048; webId=9e35977b638b80e7d08cf381f855f048; gid=yYiSqJK8ff8dyYiSqJK8KWhD2jvSdvE3WlVuUDlkJIDyxU28Cu97U288824284Y8KJJ2WDqS; abRequestId=9e35977b638b80e7d08cf381f855f048; webBuild=4.17.2; xsecappid=xhs-pc-web; web_session=040069b4a5e736438e5ec39a63344b0b4cd880; unread={%22ub%22:%22664f22c2000000000c018c29%22%2C%22ue%22:%226653f3f30000000005006549%22%2C%22uc%22:27}; websectiga=10f9a40ba454a07755a08f27ef8194c53637eba4551cf9751c009d9afb564467; sec_poison_id=0d800264-3603-4fd7-bc4a-b2e12ed32321"
        return XhsClientPLUS(cookie, sign=sign)



os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'

emoji_list = ["😀","😁","😂","🤣","😄","😅","😆","😎","🤑","🧏","👨"]
ly_id = 606

if __name__ == '__main__':
    cl = XhsCli.get_client()
    #
    list = DB_UTILS.DB.query(Comment).filter(Comment.status == 0).all()
    for u in list:
        print(u.id)
        try:
            print(cl.like_comment(note_id=u.note_id, comment_id=u.comment_id))
        except Exception as e:
            print(e)
        sleep_time = random.uniform(4, 5)
        time.sleep(sleep_time)