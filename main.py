import os
from time import sleep
from playwright.sync_api import sync_playwright
from plus.core_plus import XhsClientPLUS

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

class XhsCli():

    @staticmethod
    def get_client():
        cookie = ("a1=18899128b85l5n8twc100c9axk1spz7kx7ki6j47f50000247056; webId=15840f0fd45c7d6368c7ee14b82e26cf; gid=yYYjjyJYj2CKyYYjjyJYDWV4Y212IY9ESy88TWiSj0CTy328MUuWTK888J4W82K8qYKJ4W2f; gid.sign=0bbbu1JE19T6P9g0+QaoPEwa61M=; abRequestId=15840f0fd45c7d6368c7ee14b82e26cf; customerClientId=106623081685495; customer-sso-sid=662a3091300000000000000236fecfb13cc3fac0; x-user-id-creator.xiaohongshu.com=641a8696000000001201269c; access-token-creator.xiaohongshu.com=customer.ares.AT-9d03357963a244878db71c7cc47e9c20-3bbd6fac68ef4c31ac1714f64f361526; web_session=040069b4a5e736438e5e8db173344b290f4ba6; websectiga=634d3ad75ffb42a2ade2c5e1705a73c845837578aeb31ba0e442d75c648da36a; sec_poison_id=6557c200-a45a-4c63-9fb9-af89bb8a5946; acw_tc=438041a218a18d743ec09ffe38fd6ae3d9455ea0ac7660fd86f8a78236038b4f; webBuild=4.16.1; xsecappid=xhs-pc-web; unread={%22ub%22:%226641e1f9000000001e024579%22%2C%22ue%22:%22664caed1000000001500bfe9%22%2C%22uc%22:22}")
        return XhsClientPLUS(cookie, sign=sign)

list = ["6008201e000000000100a78e"]
from tests.utils import beauty_print
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
cl = XhsCli.get_client()
for item in list:
    # print(cl.get_user_info(user_id=item))
    cl.save_user_all_notes(user_id=item, dir_path="D:/xhs2", crawl_interval = 0)