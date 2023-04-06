<div align="center">

<h1 align="center">
🍰xhs
</h1>

[![](https://img.shields.io/github/license/ReaJason/17wanxiaoCheckin-Actions "协议")](https://github.com/ReaJason/17wanxiaoCheckin/blob/master/LICENSE)
[![](https://github.com/ReaJason/xhs/actions/workflows/doc.yml/badge.svg)](https://reajason.github.io/xhs/)
[![](https://github.com/ReaJason/xhs/actions/workflows/test.yml/badge.svg)](https://github.com/ReaJason/xhs/actions/workflows/test.yml)
[![](https://github.com/ReaJason/xhs/actions/workflows/pypi.yml/badge.svg)](https://github.com/ReaJason/xhs/actions/workflows/pypi.yml)

</div>

**xhs** is a crawling tool designed to extract data from [xiaohongshu website](https://www.xiaohongshu.com/explore)

# Usage

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

# more functions in development
```

Please refer to the [document(WIP)](https://reajason.github.io/xhs/) for more API references.

use signature function:

```python
# sign get request
>>> from xhs import help
>>> help.sign("/api/sns/web/v1/user/otherinfo?target_user_id=5ff0e6410000000001008400")
{'x-s': '1l5LsiTlZYavOYwvOid6OlU6OisCZ6dBZjvL1gsCOg13', 'x-t': '1680701208022'}

# sign post request
>>> help.sign("/api/sns/web/v1/feed", {"source_note_id": "63db8819000000001a01ead1"})
{'x-s': 'sY5LOg9WOYFKsYFWOBcis2MlsiFCsjMb0jTKZja6OjA3', 'x-t': '1680701310666'}

# get search_id parameter
>>> help.get_search_id()
'2BHU39J8HCTIW665YHFCW'
```
