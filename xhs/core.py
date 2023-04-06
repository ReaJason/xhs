import json
from enum import Enum

import requests

from xhs.exception import DataFetchError

from .help import get_search_id, sign


class FeedType(Enum):
    # 推荐
    RECOMMEND = "homefeed_recommend"
    # 穿搭
    FASION = "homefeed.fashion_v3"
    # 美食
    FOOD = "homefeed.food_v3"
    # 彩妆
    COSMETICS = "homefeed.cosmetics_v3"
    # 影视
    MOVIE = "homefeed.movie_and_tv_v3"
    # 职场
    CAREER = "homefeed.career_v3"
    # 情感
    EMOTION = "homefeed.love_v3"
    # 家居
    HOURSE = "homefeed.household_product_v3"
    # 游戏
    GAME = "homefeed.gaming_v3"
    # 旅行
    TRAVEL = "homefeed.travel_v3"
    # 健身
    FITNESS = "homefeed.fitness_v3"


class XhsClient:

    def __init__(self,
                 cookie: str | None = None,
                 user_agent: str | None = None,
                 timeout: int | None = None,
                 proxies: dict | None = None):
        self._user_agent = user_agent or ("Mozilla/5.0 "
                                          "(Windows NT 10.0; Win64; x64) "
                                          "AppleWebKit/537.36 "
                                          "(KHTML, like Gecko) "
                                          "Chrome/111.0.0.0 Safari/537.36")
        self._cookie = cookie
        self._proxies = proxies
        self._session: requests.Session = requests.session()
        self._timeout = timeout or 10
        self._host = "https://edith.xiaohongshu.com"

    def set_cookie(self, cookie: str):
        self._cookie = cookie

    def get_cookie(self):
        return self._cookie

    def get_user_agent(self):
        return self._user_agent

    def set_user_agent(self, user_agent: str):
        self._user_agent = user_agent

    def get_proxies(self):
        return self._proxies

    def set_proxies(self, proxies: dict):
        self._proxies = proxies

    def get_timeout(self):
        return self._timeout

    def set_timeout(self, timeout):
        self._timeout = timeout

    def _pre_headers(self, url: str, data: dict | None = None):
        assert self._cookie
        signs = sign(url, data)
        return {
            "User-Agent": self._user_agent,
            "cookie": self._cookie,
            "x-s": signs["x-s"],
            "x-t": signs["x-t"],
            "Content-Type": "application/json"
        }

    def request(self, method, url, **kwargs):
        response = self._session.request(
            method, url, timeout=self._timeout,
            proxies=self._proxies, **kwargs)
        data = response.json()
        if data["success"]:
            return data["data"]
        else:
            raise DataFetchError(data.get("msg", None))

    def get(self, uri: str, params: dict | None = None):
        final_uri = uri
        if isinstance(params, dict):
            final_uri = (f"{uri}?"
                         f"{'&'.join([f'{k}={v}'for k,v in params.items()])}")
        headers = self._pre_headers(final_uri)
        return self.request(method="GET", url=f"{self._host}{final_uri}",
                            headers=headers)

    def post(self, uri: str, data: dict):
        headers = self._pre_headers(uri, data)
        json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        return self.request(method="POST", url=f"{self._host}{uri}",
                            data=json_str.encode("utf-8"),
                            headers=headers)

    def get_note_by_id(self, note_id: str):
        data = {"source_note_id": note_id}
        uri = "/api/sns/web/v1/feed"
        res = self.post(uri, data)
        return res["items"][0]

    def get_self_info(self):
        uri = "/api/sns/web/v1/user/selfinfo"
        res = self.get(uri)
        return res

    def get_user_info(self, user_id: str):
        uri = "/api/sns/web/v1/user/otherinfo"
        params = {
            "target_user_id": user_id
        }
        return self.get(uri, params)

    def get_home_feed(self, feed_type: FeedType):
        uri = "/api/sns/web/v1/homefeed"
        data = {
            "cursor_score": "",
            "num": 40,
            "refresh_type": 1,
            "note_index": 0,
            "unread_begin_note_id": "",
            "unread_end_note_id": "",
            "unread_note_count": 0,
            "category": feed_type.value
        }
        return self.post(uri, data)

    def get_note_by_keyword(self, keyword: str):
        uri = "/api/sns/web/v1/search/notes"
        data = {
            "keyword": keyword,
            "page": 1,
            "page_size": 20,
            "search_id": get_search_id(),
            "sort": "general",
            "note_type": 0
        }
        return self.post(uri, data)

    def get_user_notes(self, user_id: str, cursor: str = ""):
        uri = "/api/sns/web/v1/user_posted"
        params = {
            "num": 30,
            "cursor": cursor,
            "user_id": user_id
        }
        return self.get(uri, params)
