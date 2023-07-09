from time import sleep
from xhs import XhsClient
from playwright.sync_api import sync_playwright


def get_context_page(instance, stealth_js_path):
    chromium = instance.chromium
    browser = chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 "
                   "Safari/537.36"
    )
    context.add_init_script(path=stealth_js_path)
    page = context.new_page()
    return context, page


def sign(uri, data=None, a1="", web_session=""):
    context_page.goto("https://www.xiaohongshu.com")
    cookie_list = browser_context.cookies()
    web_session_cookie = list(filter(lambda cookie: cookie["name"] == "web_session", cookie_list))
    if not web_session_cookie:
        browser_context.add_cookies([
            {'name': 'web_session', 'value': web_session, 'domain': ".xiaohongshu.com", 'path': "/"},
            {'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"}]
        )
        sleep(1)
    encrypt_params = context_page.evaluate("([url, data]) => window._webmsxyw(url, data)", [uri, data])
    return {
        "x-s": encrypt_params["X-s"],
        "x-t": str(encrypt_params["X-t"])
    }


if __name__ == '__main__':
    cookie = "please get cookie from your website"
    stealth_js_path = "/Users/reajason/ReaJason/xhs/tests/stealth.min.js"
    playwright = sync_playwright().start()
    browser_context, context_page = get_context_page(playwright, stealth_js_path)

    xhs_client = XhsClient(cookie, sign=sign)

    # get note info
    note_info = xhs_client.get_note_by_id("63db8819000000001a01ead1")

    print(note_info)

    # resource release
    playwright.stop()
