<div align="center">

<h1 align="center">
🍰xhs
</h1>

[![PyPI](https://img.shields.io/pypi/v/xhs?label=xhs)](https://pypi.org/project/xhs/)
[![](https://static.pepy.tech/badge/xhs)](https://pepy.tech/project/xhs)
[![](https://img.shields.io/github/license/ReaJason/xhs)](https://github.com/ReaJason/xhs/blob/master/LICENSE)
[![Tencent QQ](https://img.shields.io/badge/QQ-668689006-%2312B7F5?logo=tencentqq&logoColor=white)](https://qm.qq.com/cgi-bin/qm/qr?k=ClAygjOnEiOotOGzu6yQ8ZhWekrArAXf&jump_from=webapi&authKey=Gje6CcffTA1untyXfv/Pitt4aXQ0m2I/4p0PeTaRYCueTgwM5NwT842miLW4zGL/)
<br /> [![](https://github.com/ReaJason/xhs/actions/workflows/doc.yml/badge.svg)](https://reajason.github.io/xhs/)
[![](https://github.com/ReaJason/xhs/actions/workflows/test.yml/badge.svg)](https://github.com/ReaJason/xhs/actions/workflows/test.yml)
[![](https://github.com/ReaJason/xhs/actions/workflows/pypi.yml/badge.svg)](https://github.com/ReaJason/xhs/actions/workflows/pypi.yml)

</div>

> **Warning**
>
> The primary purpose of this repository is to practice my Python skills. It is important to note that web crawling may
> be considered illegal, and therefore, it is crucial to refrain from exerting any pressure or engaging in unauthorized
> activities on websites.

**xhs** is a crawling tool designed to extract data from [xiaohongshu website](https://www.xiaohongshu.com/explore)

## Usage

xhs is available on PyPI:

```console
$ python -m pip install xhs
```

if you want the latest version, you can install from git:

```console
$ python -m pip install git+https://github.com/ReaJason/xhs
```

### Basic Usage 

> maybe now is more complex, Thanks [@NanmiCoder](https://github.com/NanmiCoder)


```shell
curl -O https://cdn.jsdelivr.net/gh/requireCool/stealth.min.js/stealth.min.js

pip install playwright

playwright install
```

```python
from time import sleep
from xhs import FeedType, XhsClient
from playwright.sync_api import sync_playwright


def get_context_page(playwright):
    chromium = playwright.chromium
    browser = chromium.launch(headless=True)
    browser_context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )
    browser_context.add_init_script(path="stealth.min.js")
    context_page = browser_context.new_page()
    return browser_context, context_page


playwright = sync_playwright().start()
browser_context, context_page = get_context_page(playwright)

cookie = "please get cookie in website"


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


xhs_client = XhsClient(cookie, sign=sign)

# get note info
note_info = xhs_client.get_note_by_id("63db8819000000001a01ead1")

# get user info
user_info = xhs_client.get_user_info("5ff0e6410000000001008400")

# get user notes
user_notes = xhs_client.get_user_notes("63273a77000000002303cc9b")

# search note
notes = xhs_client.get_note_by_keyword("小红书")

# get home recommend feed
recommend_type = FeedType.RECOMMEND
recommend_notes = xhs_client.get_home_feed(recommend_type)

# save notes file in disk
xhs_client.save_files_from_note_id("63db8819000000001a01ead1",
                                   r"C:\Users\User\Desktop"

# get user all note detail
notes = xhs_client.get_user_all_notes("5c2766b500000000050283f1")

# resource release
playwright.stop()

# more functions in development
```

Please refer to the [document(WIP)](https://reajason.github.io/xhs/) for more API references.

~~use signature function~~( it's useless ):

```python
# sign get request
>> > from xhs import help
>> > help.sign("/api/sns/web/v1/user/otherinfo?target_user_id=5ff0e6410000000001008400")
{'x-s': 'sYMlOB5W0YdvZBVvOBw6slZJZjM+ZgaUOlFisBwJslc3', 'x-t': '1683368960336',
 'x-s-common': '2UQAPsHC+aIjqArjwjHjNsQhPsHCH0rjNsQhPaHCH0P1PjhIHjIj2eHjwjQgynEDJ74AHjIj2ePjwjQhyoPTqBPT49pjHjIj2ecjwjHUN0P1PaHVHdWMH0ijHjIj2eGjwjHl+0W
 APAGhw / GIPAP9HjIj2eqjwjQAnLMV / FHMpAm88o8ycS89 / FQ7 + d + VnDkyyDF3nf4YpLRVzfSAcd4tq9l0PUHVHdWhH0ijHjIj2eDjwjFAPAPU + eHMweDANsQhP / Zjw0bR'}

                                                                                                                                                # sign post request
                                                                                                                                                >> > help.sign(
     "/api/sns/web/v1/feed", {"source_note_id": "63db8819000000001a01ead1"})
 {'x-s': '1lU6sBdUOY5WZY5Ksg9G0Yw60jwBOlFWZj5W0jM+slc3', 'x-t': '1683368998055',
  'x-s-common': '2UQAPsHC+aIjqArjwjHjNsQhPsHCH0rjNsQhPaHCH0P1PjhIHjIj2eHjwjQgynEDJ74AHjIj2ePjwjQhyoPTqBPT49pjHjIj2ecjwjHUN0P1PaHVHdWMH0ijHjIj2eGjwjHl+0W
  APAGhw / DhPeLMHjIj2eqjwjHlJbL9qFQDpLR8 + p4yn / pNq9qEzAm84AGIyd4s / 9lBpMkx + pqIyDF3q9l0PUHVHdWhH0ijHjIj2eDjwjFlP0DEw / DFPeDANsQhP / Zjw0bR
  '}

  # generate a1 and webId, but it not useful until you sign them
  >> > help.get_a1_and_web_id()
  ('187f09d3bc6wUrNpFbQ9Yc431AenpvlBJh2QIQahI50000261040', '12b49a1fd517aa8df85380e9961b6800')

  # get search_id parameter
  >> > help.get_search_id()
      '2BHU39J8HCTIW665YHFCW'
```
