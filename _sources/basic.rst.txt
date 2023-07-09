快速入门
===============================

由于 x-s 签名较复杂，因此使用 `playwright <https://playwright.dev/python/>`_ 进行模拟浏览器行为进行 js 函数调用获取签名算法，
并且其中存在大量的环境检测的行为，因此需要使用到 `stealth.min.js <https://github.com/requireCool/stealth.min.js>`_ 进行绕过。

**环境安装**:

.. code-block:: bash

    pip install xhs # 下载 xhs 包

    pip install playwright # 下载 playwright

    playwright install # 安装浏览器环境

    curl -O https://cdn.jsdelivr.net/gh/requireCool/stealth.min.js/stealth.min.js # 下载 stealth.min.js

基础使用
-----------
脚本例子看参考：`basic_usage.py <https://github.com/ReaJason/xhs/blob/master/example/basic_usage.py>`_

.. code-block:: python3

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
        stealth_js_path = "your downloaded stealth.min.js file path"
        playwright = sync_playwright().start()
        browser_context, context_page = get_context_page(playwright, stealth_js_path)

        xhs_client = XhsClient(cookie, sign=sign)

        # get note info
        note_info = xhs_client.get_note_by_id("63db8819000000001a01ead1")

        print(note_info)

        # resource release
        playwright.stop()


进阶使用
----------------
将 playwright 封装为服务端，主函数使用 requests 请求，获取签名。


环境安装
^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: bash

    pip install flask, gevent, requests

开启 Flask 签名服务
^^^^^^^^^^^^^^^^^^^^^^^^
脚本地址： `basic_sign_server <https://github.com/ReaJason/xhs/blob/master/example/basic_sign_server.py>`_

.. code-block:: python3

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


使用 XhsClient
^^^^^^^^^^^^^^^^^^^
第一次请求会失败，但是之后的请求就正常了。

脚本地址： `basic_sign_usage <https://github.com/ReaJason/xhs/blob/master/example/basic_sign_usage.py>`_

.. code-block:: python3

    import requests
    from xhs import XhsClient


    def sign(uri, data=None, a1="", web_session=""):
        # 填写自己的 flask 签名服务端口地址
        res = requests.post("http://localhost:5005",
                            json={"uri": uri, "data": data, "a1": a1, "web_session": web_session})
        signs = res.json()
        return {
            "x-s": signs["x-s"],
            "x-t": signs["x-t"]
        }


    if __name__ == '__main__':
        cookie = "please get cookie from your website"
        xhs_client = XhsClient(cookie, sign=sign)
        # get note info
        note_info = xhs_client.get_note_by_id("63db8819000000001a01ead1")
        print(note_info)
