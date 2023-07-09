from flask import Flask, request
from playwright.sync_api import sync_playwright
from gevent import monkey

monkey.patch_all()

app = Flask(__name__)


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


# 如下更改为 stealth.min.js 文件路径地址
stealth_js_path = "/Users/reajason/ReaJason/xhs/tests/stealth.min.js"
playwright = sync_playwright().start()
browser_context, context_page = get_context_page(playwright, stealth_js_path)
context_page.goto("https://www.xiaohongshu.com")


def sign(uri, data, a1, web_session):
    browser_context.add_cookies([
        {'name': 'web_session', 'value': web_session, 'domain': ".xiaohongshu.com", 'path': "/"},
        {'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"}]
    )
    encrypt_params = context_page.evaluate("([url, data]) => window._webmsxyw(url, data)", [uri, data])
    return {
        "x-s": encrypt_params["X-s"],
        "x-t": str(encrypt_params["X-t"])
    }


@app.route("/", methods=["POST"])
def hello_world():
    json = request.json
    uri = json["uri"]
    data = json["data"]
    a1 = json["a1"]
    web_session = json["web_session"]
    return sign(uri, data, a1, web_session)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005)
