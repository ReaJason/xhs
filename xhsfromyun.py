import base64
import datetime
import os
import random
import sqlite3
import time
from time import sleep

import requests
from playwright.sync_api import sync_playwright

from plus.core_plus import XhsClientPLUS
from plus.db_utils import DB_UTILS
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

con = sqlite3.connect("xhs.db")
def add(user_id, note_id, title, user_name):
    try:
        sql = f'replace INTO "xhs" ("user_id", "note_id", "title", "user_name") VALUES ("{user_id}", "{note_id}", "{title}", "{user_name}");'
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
    except Exception as e:
        print(e)

def count(user_id, note_id):
    try:
        cur = con.cursor()
        cur.execute("SELECT count(1) from xhs where user_id ='"+user_id+"' and note_id = '"+note_id+"'")
        list = cur.fetchall()
        return list[0][0] != 0
    except Exception as e:
        print(e)
def select_list(table, wsql):
    try:
        cur = con.cursor()
        cur.execute("SELECT * from "+table+" where "+ wsql+"")
        list = cur.fetchall()
        return list
    except Exception as e:
        print(e)

def select(table, wsql):
    try:
        cur = con.cursor()
        cur.execute("SELECT * from "+table+" where "+ wsql+"")
        list = cur.fetchall()
        return list[0]
    except Exception as e:
        print(e)

class XhsCli():
    @staticmethod
    def get_client():
        cookie = "a1=18899128b85l5n8twc100c9axk1spz7kx7ki6j47f50000247056; webId=15840f0fd45c7d6368c7ee14b82e26cf; gid=yYYjjyJYj2CKyYYjjyJYDWV4Y212IY9ESy88TWiSj0CTy328MUuWTK888J4W82K8qYKJ4W2f; gid.sign=0bbbu1JE19T6P9g0+QaoPEwa61M=; abRequestId=15840f0fd45c7d6368c7ee14b82e26cf; customerClientId=106623081685495; x-user-id-creator.xiaohongshu.com=641a8696000000001201269c; webBuild=4.17.2; web_session=040069b56ec5de1b76caaafa64344b95b6d93d; unread={%22ub%22:%22665094320000000015013592%22%2C%22ue%22:%226650b30300000000050049dc%22%2C%22uc%22:33}; customer-sso-sid=68c51737287096782851612473a37ceec4330635; access-token-creator.xiaohongshu.com=customer.creator.AT-68c5173728709678285161271fr2elxhpukyeinu; galaxy_creator_session_id=i33NiON6p9INMejwq0rnzRlxnb7YKOiOZ9PR; galaxy.creator.beaker.session.id=1716630293620025046551; feprobase-status=online; feprobase-status.sig=XO8DrQBuzb6IXDq0Wun41eYnvdpECuPHarbSX8ZfK1o; x-user-id-pro.xiaohongshu.com=641a8696000000001201269c; access-token-pro.xiaohongshu.com=customer.ares.AT-68c517373925953534790154ch7kz0c9zgekpbpw; access-token-pro.beta.xiaohongshu.com=customer.ares.AT-68c517373925953534790154ch7kz0c9zgekpbpw; feprofenterprise-status=online; feprofenterprise-status.sig=3p9WYWrifZLADobSghAYHQRjob7261vq12cO-Fkwyws; feproenterprisenext-status=online; feproenterprisenext-status.sig=hTuTBJuPnbmI3kQm0J125ZhHT-wY5-R1r2R1p0pOZ3M; websectiga=3633fe24d49c7dd0eb923edc8205740f10fdb18b25d424d2a2322c6196d2a4ad; acw_tc=0be35ddd52595f045fc58d775b7d20f5f19a3101e8248e7d01587b860a022415; xsecappid=pro-enterprise"
        return XhsClientPLUS(cookie, sign=sign)

def get_base(encoded_string):
    decoded_bytes = base64.b64decode(encoded_string)
    return decoded_bytes.decode('utf-8')
def get_comment_list(cl, note_id, title):
    comments_cursor = ""
    result = []
    comments_has_more = True
    while comments_has_more:
        comments_res = cl.get_note_comments(note_id, comments_cursor)
        comments_has_more = comments_res.get("has_more", False)
        comments_cursor = comments_res.get("cursor", "")
        comments = comments_res["comments"]
        for com in comments:
            try:
                # 创建datetime对象
                dt_object = datetime.datetime.fromtimestamp(com["create_time"] / 1000)

                # 格式化日期字符串
                formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
                data = cl.get_user_info(com["user_info"]["user_id"])
                base = data["basic_info"]
                gender = base.get("gender", "")
                ip_2_location = base.get("ip_location", "")
                desc = base.get("desc", "")
                if gender == 1:
                    DB_UTILS.save(Comment(note_id=note_id, title=title, content=com["content"], create_time=formatted_date, user_id=com["user_info"]["user_id"], nickname=com["user_info"]["nickname"], comment_id=com["id"], ip_location=com.get("ip_location", ""), image=com["user_info"]["image"], gender = gender, ip_2_location = ip_2_location, desc = desc, status = 0))
            except Exception as e:
                print("重复")
        time.sleep(5)
    return result
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

#  5rSb6Ziz55u45Lqy  lyxq
#  5rex5Zyz55u45Lqy  szxq
#  6YOR5bee55u45Lqy  zzxq
#  5rSb6Ziz5om+5a+56LGhCg==  lyzdx
#  5rex5Zyz5om+5a+56LGhCg==   szzdx
# 6YOR5bee5om+5a+56LGhCg==  zzzdx

keyword = get_base("5rex5Zyz55u45Lqy")

# 如果解码内容是文本，将其从字节转换为字符串
# 注意指定正确的解码字符集，通常是utf-8
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
emoji_list = ["😀","😁","😂","🤣","😄","😅","😆","😎","🤑","🧏","👨"]
if __name__ == '__main__':
    cl = XhsCli.get_client()
    for i in range(1, 16):
        data = cl.get_note_by_keyword(keyword=keyword, sort=SearchSortType.GENERAL, page=i)
        items = data["items"]
        for item in items:
            try:
                note_id = item["id"]
                try:
                    title = item["note_card"]["display_title"]
                except Exception as e:
                    title = ""
                model_type = item["model_type"]
                if model_type != "note":
                    continue
                    id = Column(Integer, primary_key=True, autoincrement=True)
                com_list = get_comment_list(cl, note_id, title)
                sleep_time = random.uniform(60, 150)
                time.sleep(sleep_time)
            except Exception as e:
                print(e)
                pass
