import os
import random
import time
from time import sleep

from apscheduler.schedulers.blocking import BlockingScheduler
from playwright.sync_api import sync_playwright
from plus.core_plus import XhsClientPLUS
from plus.db_utils import DB_UTILS, SessionLocal
from plus.model.Model import Comment, HasComments


def sign(uri, data=None, a1="", web_session=""):
    for _ in range(10):
        try:
            with sync_playwright() as playwright:
                stealth_js_path = r"D:\docker\xhs\stealth.min.js"
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
msg = "你好，想跟你认识一下"
def get_random(items):
    return items[random.randint(0, len(items) - 1)]


class XhsCli():

    @staticmethod
    def get_client():
        cookie = "a1=18fc3260659yceywi7ojzg2nb1hxztup07pp5vbbo50000545048; webId=9e35977b638b80e7d08cf381f855f048; gid=yYiSqJK8ff8dyYiSqJK8KWhD2jvSdvE3WlVuUDlkJIDyxU28Cu97U288824284Y8KJJ2WDqS; abRequestId=9e35977b638b80e7d08cf381f855f048; webBuild=4.17.2; web_session=040069b4a5e736438e5ec39a63344b0b4cd880; unread={%22ub%22:%22664f22c2000000000c018c29%22%2C%22ue%22:%226653f3f30000000005006549%22%2C%22uc%22:27}; customerClientId=833153284526087; customer-sso-sid=6656d39148000000000000028421c589f4c6a109; x-user-id-pro.xiaohongshu.com=65d1a47e000000000401de08; access-token-pro.xiaohongshu.com=customer.ares.AT-68c517374314059664520991zdcqfhf5awer23dj; access-token-pro.beta.xiaohongshu.com=customer.ares.AT-68c517374314059664520991zdcqfhf5awer23dj; websectiga=82e85efc5500b609ac1166aaf086ff8aa4261153a448ef0be5b17417e4512f28; sec_poison_id=5e998d9c-13ac-4ffe-b543-90fd2c1682ac; acw_tc=3c3e5eb370da71f149250ccf33184f61a1e60fb22abd4aec3d0dd80760087529; xsecappid=xhs-pc-web"
        return XhsClientPLUS(cookie, sign=sign)


def comment():
    cl = XhsCli.get_client()
    del_note_id = []
    cl.delete_note()
    list = DB_UTILS.DB.query(Comment).filter(Comment.gender == 1).filter(Comment.status == 0).all()
    for u in list:
        try:
            db = SessionLocal()
            c = db.query(HasComments).filter(HasComments.comment_id == u.comment_id).all()
            if del_note_id.__contains__(u.note_id):
                db.add(HasComments(comment_id=u.comment_id))
                db.commit()
                continue
            if len(c)  == 0:
                print(cl.comment_user(u.note_id, u.comment_id, "dd"))
                db.add(HasComments(comment_id=u.comment_id))
                db.commit()
                sleep_time = random.uniform(10, 20)
                time.sleep(sleep_time)
            db.close()
        except Exception as e:
            e = e.args[0]
            if (e.get("code") == -9106 or e.get("code") == -9126):
                # del_note_id.append(u.note_id)
                db.add(HasComments(comment_id=u.comment_id))
                db.commit()
            print(e)
if __name__ == '__main__':
    comment()