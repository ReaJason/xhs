import datetime
import json
from time import sleep

from playwright.sync_api import sync_playwright

from xhs import DataFetchError, XhsClient


def sign(uri, data=None, a1="", web_session=""):
    for _ in range(10):
        try:
            with sync_playwright() as playwright:
                stealth_js_path = "/Users/reajason/ReaJason/xhs/tests/stealth.min.js"
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


if __name__ == '__main__':
    xhs_client = XhsClient(sign=sign)
    print(datetime.datetime.now())
    phone = "login phone num"
    res = xhs_client.send_code(phone)
    print("验证码发送成功~")
    code = input("请输入验证码：")
    token = ""
    while True:
        try:
            check_res = xhs_client.check_code(phone, code)
            token = check_res["mobile_token"]
            break
        except DataFetchError as e:
            print(e)
            code = input("请输入验证码：")
    login_res = xhs_client.login_code(phone, token)
    print(json.dumps(login_res, indent=4))
    print("当前 cookie：" + xhs_client.cookie)

    print(xhs_client.get_self_info())
