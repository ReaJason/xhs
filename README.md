<div align="center">

<h1 align="center">
🍰xhs
</h1>

[![](https://static.pepy.tech/badge/xhs)](https://pepy.tech/project/xhs)
[![](https://img.shields.io/github/license/ReaJason/xhs)](https://github.com/ReaJason/xhs/blob/master/LICENSE)
[![](https://github.com/ReaJason/xhs/actions/workflows/doc.yml/badge.svg)](https://reajason.github.io/xhs/)
[![](https://github.com/ReaJason/xhs/actions/workflows/test.yml/badge.svg)](https://github.com/ReaJason/xhs/actions/workflows/test.yml)
[![](https://github.com/ReaJason/xhs/actions/workflows/pypi.yml/badge.svg)](https://github.com/ReaJason/xhs/actions/workflows/pypi.yml)

</div>

> **Warning**
>
> This is in expriemental, so the api is not stable, every update should be cautious

**xhs** is a crawling tool designed to extract data from [xiaohongshu website](https://www.xiaohongshu.com/explore)

## Usage

xhs is available on PyPI:

```console
$ python -m pip install xhs
```

basic usage:

```python
from xhs import FeedType, XhsClient

cookie = "please get cookie in website"
xhs_client = XhsClient(cookie)

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

# more functions in development
```

Please refer to the [document(WIP)](https://reajason.github.io/xhs/) for more API references.

use signature function:

```python
# sign get request
>>> from xhs import help
>>> help.sign("/api/sns/web/v1/user/otherinfo?target_user_id=5ff0e6410000000001008400")
{'x-s': 'sYMlOB5W0YdvZBVvOBw6slZJZjM+ZgaUOlFisBwJslc3', 'x-t': '1683368960336', 'x-s-common': '2UQAPsHC+aIjqArjwjHjNsQhPsHCH0rjNsQhPaHCH0P1PjhIHjIj2eHjwjQgynEDJ74AHjIj2ePjwjQhyoPTqBPT49pjHjIj2ecjwjHUN0P1PaHVHdWMH0ijHjIj2eGjwjHl+0W
APAGhw/GIPAP9HjIj2eqjwjQAnLMV/FHMpAm88o8ycS89/FQ7+d+VnDkyyDF3nf4YpLRVzfSAcd4tq9l0PUHVHdWhH0ijHjIj2eDjwjFAPAPU+eHMweDANsQhP/Zjw0bR'}


# sign post request
>>> help.sign("/api/sns/web/v1/feed", {"source_note_id": "63db8819000000001a01ead1"})
{'x-s': '1lU6sBdUOY5WZY5Ksg9G0Yw60jwBOlFWZj5W0jM+slc3', 'x-t': '1683368998055', 'x-s-common': '2UQAPsHC+aIjqArjwjHjNsQhPsHCH0rjNsQhPaHCH0P1PjhIHjIj2eHjwjQgynEDJ74AHjIj2ePjwjQhyoPTqBPT49pjHjIj2ecjwjHUN0P1PaHVHdWMH0ijHjIj2eGjwjHl+0W
APAGhw/DhPeLMHjIj2eqjwjHlJbL9qFQDpLR8+p4yn/pNq9qEzAm84AGIyd4s/9lBpMkx+pqIyDF3q9l0PUHVHdWhH0ijHjIj2eDjwjFlP0DEw/DFPeDANsQhP/Zjw0bR'}

# generate a1 and webId, but it not useful until you sign them
>>> help.get_a1_and_web_id()
('187f09d3bc6wUrNpFbQ9Yc431AenpvlBJh2QIQahI50000261040', '12b49a1fd517aa8df85380e9961b6800')

# get search_id parameter
>>> help.get_search_id()
'2BHU39J8HCTIW665YHFCW'
```

## Donate

[![](https://afdian.net/static/img/logo/logo.png)](https://afdian.net/a/reajason)
