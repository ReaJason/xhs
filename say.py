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

is_115 = False
class XhsCli():

    @staticmethod
    def get_client():
        cookie155 = "acw_tc=57c2bf4f0d4411c4596c4cd678f1f9e3025db32fd043d21b6c00f6b9e303739a; feprobase-status=online; feprobase-status.sig=XO8DrQBuzb6IXDq0Wun41eYnvdpECuPHarbSX8ZfK1o; a1=18fc90161fdpuprkngdcokf201ql5v6f4dtn2v30k50000976864; webId=1b632c5517227932d352b2dec813b3f9; gid=yYiSj8yK4y4KyYiSj8yKyfhqifU7UFTIkfSl98TTiJ8yAI2812hKiJ888jWKYK48Dd8iDyfy; customerClientId=128273299738195; customer-sso-sid=66585261360000000000000775c29e9ed78c2d69; x-user-id-pro.xiaohongshu.com=641a8696000000001201269c; access-token-pro.xiaohongshu.com=customer.ares.AT-68c517374734966459667916xgyj3pjeitxvcuju; access-token-pro.beta.xiaohongshu.com=customer.ares.AT-68c517374734966459667916xgyj3pjeitxvcuju; feprofenterprise-status=online; feprofenterprise-status.sig=3p9WYWrifZLADobSghAYHQRjob7261vq12cO-Fkwyws; xsecappid=pro-enterprise"
        cookie = 'feprobase-status=online; feprobase-status.sig=XO8DrQBuzb6IXDq0Wun41eYnvdpECuPHarbSX8ZfK1o; feprofenterprise-status=online; feprofenterprise-status.sig=3p9WYWrifZLADobSghAYHQRjob7261vq12cO-Fkwyws; a1=18fc3260659yceywi7ojzg2nb1hxztup07pp5vbbo50000545048; webId=9e35977b638b80e7d08cf381f855f048; gid=yYiSqJK8ff8dyYiSqJK8KWhD2jvSdvE3WlVuUDlkJIDyxU28Cu97U288824284Y8KJJ2WDqS; abRequestId=9e35977b638b80e7d08cf381f855f048; webBuild=4.17.2; web_session=040069b4a5e736438e5ec39a63344b0b4cd880; unread={%22ub%22:%22664f22c2000000000c018c29%22%2C%22ue%22:%226653f3f30000000005006549%22%2C%22uc%22:27}; websectiga=10f9a40ba454a07755a08f27ef8194c53637eba4551cf9751c009d9afb564467; sec_poison_id=0d800264-3603-4fd7-bc4a-b2e12ed32321; acw_tc=2e4bedb673bc00107a25e19575bf94a2d036c4ca9b5dfd544fcded6f5948d463; customerClientId=833153284526087; customer-sso-sid=6656d39148000000000000028421c589f4c6a109; x-user-id-pro.xiaohongshu.com=65d1a47e000000000401de08; access-token-pro.xiaohongshu.com=customer.ares.AT-68c517374314059664520991zdcqfhf5awer23dj; access-token-pro.beta.xiaohongshu.com=customer.ares.AT-68c517374314059664520991zdcqfhf5awer23dj; feproenterprisenext-status=online; feproenterprisenext-status.sig=hTuTBJuPnbmI3kQm0J125ZhHT-wY5-R1r2R1p0pOZ3M; xsecappid=pro-enterprise'
        return XhsClientPLUS(cookie155 if is_115 else cookie, sign=sign)

id = 15
id_155 = 40 - 110
def run():
    cl = XhsCli.get_client()
    if is_115:
        list = DB_UTILS.DB.query(Comment).filter(Comment.gender == 1).filter(Comment.status_115 == 0).all()
    else:
        list = DB_UTILS.DB.query(Comment).filter(Comment.gender == 1).filter(Comment.status == 0).all()
    for u in list:
        try:
            print(cl.send(u.user_id, msg))
            db = SessionLocal()
            if is_115:
                db.query(Comment).filter(Comment.id == u.id).update({"status_115":1 })
            else:
                db.query(Comment).filter(Comment.id == u.id).update({"status":1 })
            db.commit()
            db.close()
        except Exception as e:
            print(e)

if __name__ == '__main__':
    run()