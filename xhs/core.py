import json
import os
import re
import time
from enum import Enum
from typing import NamedTuple
from datetime import datetime

import requests

from xhs.exception import DataFetchError, IPBlockError, SignError, ErrorEnum

from .help import (
    cookie_jar_to_cookie_str,
    download_file,
    get_imgs_url_from_note,
    get_search_id,
    get_valid_path_name,
    get_video_url_from_note,
    sign,
    update_session_cookies_from_cookie,
)


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


class NoteType(Enum):
    NORMAL = "normal"
    VIDEO = "video"


class SearchSortType(Enum):
    """serach sort type"""

    # default
    GENERAL = "general"
    # most popular
    MOST_POPULAR = "popularity_descending"
    # Latest
    LATEST = "time_descending"


class SearchNoteType(Enum):
    """search note type"""

    # default
    ALL = 0
    # only video
    VIDEO = 1
    # only image
    IMAGE = 2


class Note(NamedTuple):
    """note typle"""

    note_id: str
    title: str
    desc: str
    type: str
    user: dict
    img_urls: list
    video_url: str
    tag_list: list
    at_user_list: list
    collected_count: str
    comment_count: str
    liked_count: str
    share_count: str
    time: int
    last_update_time: int


class XhsClient:
    def __init__(
            self, cookie=None, user_agent=None, timeout=10, proxies=None, sign=None
    ):
        """constructor"""
        self.proxies = proxies
        self.__session: requests.Session = requests.session()
        self.timeout = timeout
        self.sign = sign
        self._host = "https://edith.xiaohongshu.com"
        self.home = "https://www.xiaohongshu.com"
        user_agent = user_agent or (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/111.0.0.0 Safari/537.36"
        )
        self.__session.headers = {
            "user-agent": user_agent,
            "Content-Type": "application/json",
        }
        self.cookie = cookie

    @property
    def cookie(self):
        return cookie_jar_to_cookie_str(self.__session.cookies)

    @cookie.setter
    def cookie(self, cookie: str):
        update_session_cookies_from_cookie(self.__session, cookie)
        if "web_session" not in self.cookie_dict:
            self.activate()

    @property
    def cookie_dict(self):
        return requests.utils.dict_from_cookiejar(self.session.cookies)

    @property
    def session(self):
        return self.__session

    @property
    def user_agent(self):
        return self.__session.headers.get("user-agent")

    @user_agent.setter
    def user_agent(self, user_agent: str):
        self.__session.headers.update({"user-agent": user_agent})

    def _pre_headers(self, url: str, data=None, is_creator: bool = False):
        if is_creator:
            signs = sign(url, data, a1=self.cookie_dict.get("a1"))
            self.__session.headers.update({"x-s": signs["x-s"]})
            self.__session.headers.update({"x-t": signs["x-t"]})
            self.__session.headers.update({"x-s-common": signs["x-s-common"]})
        else:
            self.__session.headers.update(
                self.sign(
                    url,
                    data,
                    a1=self.cookie_dict.get("a1"),
                    web_session=self.cookie_dict.get("web_session"),
                )
            )

    def request(self, method, url, **kwargs):
        response = self.__session.request(
            method, url, timeout=self.timeout, proxies=self.proxies, **kwargs
        )
        if not len(response.text):
            return response
        data = response.json()
        if data.get("success"):
            return data.get("data", data.get("success"))
        elif data["code"] == ErrorEnum.IP_BLOCK.value.code:
            raise IPBlockError(ErrorEnum.IP_BLOCK.value.msg)
        elif data["code"] == ErrorEnum.SIGN_FAULT.value.code:
            raise SignError(ErrorEnum.SIGN_FAULT.value.msg)
        else:
            raise DataFetchError(data)

    def get(self, uri: str, params=None, is_creator: bool = False, **kwargs):
        final_uri = uri
        if isinstance(params, dict):
            final_uri = f"{uri}?" f"{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        self._pre_headers(final_uri, is_creator=is_creator)
        return self.request(method="GET", url=f"{self._host}{final_uri}", **kwargs)

    def post(self, uri: str, data: dict, is_creator: bool = False, **kwargs):
        self._pre_headers(uri, data, is_creator=is_creator)
        json_str = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        return self.request(
            method="POST", url=f"{self._host}{uri}", data=json_str.encode("utf-8"), **kwargs
        )

    def get_note_by_id(self, note_id: str):
        """
        :param note_id: note_id you want to fetch
        :type note_id: str
        :rtype: dict
        """
        data = {"source_note_id": note_id}
        uri = "/api/sns/web/v1/feed"
        res = self.post(uri, data)
        return res["items"][0]["note_card"]

    def get_note_by_id_from_html(self, note_id: str):
        """get note info from "https://www.xiaohongshu.com/explore/" + note_id,
        and the return obj is equal to get_note_by_id

        :param note_id: note_id you want to fetch
        :type note_id: str
        """

        def camel_to_underscore(key):
            return re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()

        def transform_json_keys(json_data):
            data_dict = json.loads(json_data)
            dict_new = {}
            for key, value in data_dict.items():
                new_key = camel_to_underscore(key)
                if not value:
                    dict_new[new_key] = value
                elif isinstance(value, dict):
                    dict_new[new_key] = transform_json_keys(json.dumps(value))
                elif isinstance(value, list):
                    dict_new[new_key] = [
                        transform_json_keys(json.dumps(item))
                        if (item and isinstance(item, dict))
                        else item
                        for item in value
                    ]
                else:
                    dict_new[new_key] = value
            return dict_new

        url = "https://www.xiaohongshu.com/explore/" + note_id
        res = self.session.get(url, headers={"user-agent": self.user_agent})
        html = res.text
        state = re.findall(r"window.__INITIAL_STATE__=({.*})</script>", html)[
            0
        ].replace("undefined", '""')
        if state != "{}":
            note_dict = transform_json_keys(state)
            return note_dict["note"]["note"]
        elif ErrorEnum.IP_BLOCK.value in html:
            raise IPBlockError(ErrorEnum.IP_BLOCK.value)
        raise DataFetchError(html)

    def report_note_metrics(
            self,
            note_id: str,
            note_type: int,
            note_user_id: str,
            viewer_user_id: str,
            followed_author=0,
            report_type=1,
            stay_seconds=0,
    ):
        """report note stay seconds and other interaction info

        :param note_id: note_id which you want to report
        :type note_id: str
        :param note_type: input value -> 1: note is images, 2: note is video
        :type note_type: int
        :param note_user_id: note author id
        :type note_user_id: str
        :param viewer_user_id: report user id
        :type viewer_user_id: str
        :param followed_author: 1: the viewer user follow note's author, 0: the viewer user don't follow note's author
        :type followed_author: int
        :param report_type: 1: the first report, 2: the second report, so you must report twice, defaults to 1
        :type report_type: int, optional
        :param stay_seconds: report metric -> note you stay seconds, defaults to 0
        :type stay_seconds: int, optional
        :return: same as api
        :rtype: dict
        """
        uri = "/api/sns/web/v1/note/metrics_report"
        data = {
            "note_id": note_id,
            "note_type": note_type,
            "report_type": report_type,
            "stress_test": False,
            "viewer": {"user_id": viewer_user_id, "followed_author": followed_author},
            "author": {"user_id": note_user_id},
            "interaction": {"like": 0, "collect": 0, "comment": 0, "comment_read": 0},
            "note": {"stay_seconds": stay_seconds},
            "other": {"platform": "web"},
        }
        return self.post(uri, data)

    def save_files_from_note_id(self, note_id: str, dir_path: str):
        """this function will fetch note and save file in dir_path/note_title

        :param note_id: note_id that you want to fetch
        :type note_id: str
        :param dir_path: in fact, files will be stored in your dir_path/note_title directory
        :type dir_path: str
        """
        note = self.get_note_by_id(note_id)

        title = get_valid_path_name(note["title"])

        if not title:
            title = note_id

        new_dir_path = os.path.join(dir_path, title)
        if not os.path.exists(new_dir_path):
            os.mkdir(new_dir_path)

        if note["type"] == NoteType.VIDEO.value:
            video_url = get_video_url_from_note(note)
            video_filename = os.path.join(new_dir_path, f"{title}.mp4")
            download_file(video_url, video_filename)
        else:
            img_urls = get_imgs_url_from_note(note)
            for index, img_url in enumerate(img_urls):
                img_file_name = os.path.join(new_dir_path, f"{title}{index}.png")
                download_file(img_url, img_file_name)

    def get_self_info(self):
        uri = "/api/sns/web/v1/user/selfinfo"
        return self.get(uri)

    def get_self_info2(self):
        uri = "/api/sns/web/v2/user/me"
        return self.get(uri)

    def get_user_info(self, user_id: str):
        """
        :param user_id: user_id you want fetch
        :type user_id: str
        :rtype: dict
        """
        uri = "/api/sns/web/v1/user/otherinfo"
        params = {"target_user_id": user_id}
        return self.get(uri, params)

    def get_home_feed_category(self):
        uri = "/api/sns/web/v1/homefeed/category"
        return self.get(uri)["categories"]

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
            "category": feed_type.value,
        }
        return self.post(uri, data)

    def get_search_suggestion(self, keyword: str):
        uri = "/api/sns/web/v1/sug/recommend"
        params = {"keyword": keyword}
        return [sug["text"] for sug in self.get(uri, params)["sug_items"]]

    def get_note_by_keyword(
            self,
            keyword: str,
            page: int = 1,
            page_size: int = 20,
            sort: SearchSortType = SearchSortType.GENERAL,
            note_type: SearchNoteType = SearchNoteType.ALL,
    ):
        """search note by keyword

        :param keyword: what notes you want to search
        :type keyword: str
        :param page: page number, defaults to 1
        :type page: int, optional
        :param page_size: page size, defaults to 20
        :type page_size: int, optional
        :param sort: sort ordering, defaults to SearchSortType.GENERAL.
        :type sort: SearchSortType, optional
        :param note_type: note type, defaults to SearchNoteType.ALL.
        :type note_type: SearchNoteType, optional
        :return: {has_more: true, items: []}
        :rtype: dict
        """
        uri = "/api/sns/web/v1/search/notes"
        data = {
            "keyword": keyword,
            "page": page,
            "page_size": page_size,
            "search_id": get_search_id(),
            "sort": sort.value,
            "note_type": note_type.value,
        }
        return self.post(uri, data)

    def get_user_notes(self, user_id: str, cursor: str = ""):
        """get user notes just have simple info

        :param user_id: user_id you want to fetch
        :type user_id: str
        :param cursor: return info has this argument, defaults to ""
        :type cursor: str, optional
        :return: {cursor:"", has_more:true,notes:[{cover:{},display_title:"",interact_info:{},note_id:"",type:"video"}]}
        :rtype: dict
        """
        uri = "/api/sns/web/v1/user_posted"
        params = {"num": 30, "cursor": cursor, "user_id": user_id}
        return self.get(uri, params)

    def get_user_all_notes(self, user_id: str, crawl_interval: int = 1):
        """get user all notes with more info, abnormal notes will be ignored

        :param user_id: user_id you want to fetch
        :type user_id: str
        :param crawl_interval: sleep seconds, defaults to 1
        :type crawl_interval: int, optional
        :return: note info
        :rtype: list[Note]
        """
        has_more = True
        cursor = ""
        result = []
        while has_more:
            res = self.get_user_notes(user_id, cursor)
            has_more = res["has_more"]
            cursor = res["cursor"]
            note_ids = map(lambda item: item["note_id"], res["notes"])

            for note_id in note_ids:
                try:
                    note = self.get_note_by_id(note_id)
                except DataFetchError as e:
                    if ErrorEnum.NOTE_ABNORMAL.value.code == e.error.get("code"):
                        continue
                    else:
                        raise
                interact_info = note["interact_info"]
                note_info = Note(
                    note_id=note["note_id"],
                    title=note["title"],
                    desc=note["desc"],
                    type=note["type"],
                    user=note["user"],
                    img_urls=get_imgs_url_from_note(note),
                    video_url=get_video_url_from_note(note),
                    tag_list=note["tag_list"],
                    at_user_list=note["at_user_list"],
                    collected_count=interact_info["collected_count"],
                    comment_count=interact_info["comment_count"],
                    liked_count=interact_info["liked_count"],
                    share_count=interact_info["share_count"],
                    time=note["time"],
                    last_update_time=note["last_update_time"],
                )
                result.append(note_info)
                time.sleep(crawl_interval)
        return result

    def get_note_comments(self, note_id: str, cursor: str = ""):
        """get note comments

        :param note_id: note id you want to fetch
        :type note_id: str
        :param cursor: last you get cursor, defaults to ""
        :type cursor: str, optional
        :rtype: dict
        """
        uri = "/api/sns/web/v2/comment/page"
        params = {"note_id": note_id, "cursor": cursor}
        return self.get(uri, params)

    def get_note_sub_comments(
            self, note_id: str, root_comment_id: str, num: int = 30, cursor: str = ""
    ):
        """get note sub comments

        :param note_id: note id you want to fetch
        :type note_id: str
        :param root_comment_id: parent comment id
        :type root_comment_id: str
        :param num: recommend 30, if num greater 30, it only returns 30 comments
        :type num: int
        :param cursor: last you get cursor, defaults to ""
        :type cursor: str optional
        :rtype: dict
        """
        uri = "/api/sns/web/v2/comment/sub/page"
        params = {
            "note_id": note_id,
            "root_comment_id": root_comment_id,
            "num": num,
            "cursor": cursor,
        }
        return self.get(uri, params)

    def get_note_all_comments(self, note_id: str, crawl_interval: int = 1):
        """get note all comments include sub comments

        :param crawl_interval: crawl interval for fetch
        :param note_id: note id you want to fetch
        :type note_id: str
        """
        result = []
        comments_has_more = True
        comments_cursor = ""
        while comments_has_more:
            comments_res = self.get_note_comments(note_id, comments_cursor)
            comments_has_more = comments_res.get("has_more", False)
            comments_cursor = comments_res.get("cursor", "")
            comments = comments_res["comments"]
            for comment in comments:
                result.append(comment)
                cur_sub_comment_count = int(comment["sub_comment_count"])
                cur_sub_comments = comment["sub_comments"]
                result.extend(cur_sub_comments)
                sub_comments_has_more = (
                        comment["sub_comment_has_more"]
                        and len(cur_sub_comments) < cur_sub_comment_count
                )
                sub_comment_cursor = comment["sub_comment_cursor"]
                while sub_comments_has_more:
                    page_num = 30
                    sub_comments_res = self.get_note_sub_comments(
                        note_id, comment["id"], num=page_num, cursor=sub_comment_cursor
                    )
                    sub_comments = sub_comments_res["comments"]
                    sub_comments_has_more = (
                            sub_comments_res["has_more"] and len(sub_comments) == page_num
                    )
                    sub_comment_cursor = sub_comments_res["cursor"]
                    result.extend(sub_comments)
                    time.sleep(crawl_interval)
            time.sleep(crawl_interval)
        return result

    def comment_note(self, note_id: str, content: str):
        """comment a note

        :rtype: dict
        """
        uri = "/api/sns/web/v1/comment/post"
        data = {"note_id": note_id, "content": content, "at_users": []}
        return self.post(uri, data)

    def delete_note_comment(self, note_id: str, comment_id: str):
        uri = "/api/sns/web/v1/comment/delete"
        data = {"note_id": note_id, "comment_id": comment_id}
        return self.post(uri, data)

    def comment_user(self, note_id: str, comment_id: str, content: str):
        """
        :rtype: dict
        """
        uri = "/api/sns/web/v1/comment/post"
        data = {
            "note_id": note_id,
            "content": content,
            "target_comment_id": comment_id,
            "at_users": [],
        }
        return self.post(uri, data)

    def follow_user(self, user_id: str):
        uri = "/api/sns/web/v1/user/follow"
        data = {"target_user_id": user_id}
        return self.post(uri, data)

    def unfollow_user(self, user_id: str):
        uri = "/api/sns/web/v1/user/unfollow"
        data = {"target_user_id": user_id}
        return self.post(uri, data)

    def collect_note(self, note_id: str):
        uri = "/api/sns/web/v1/note/collect"
        data = {"note_id": note_id}
        return self.post(uri, data)

    def uncollect_note(self, note_id: str):
        uri = "/api/sns/web/v1/note/uncollect"
        data = {"note_ids": note_id}
        return self.post(uri, data)

    def like_note(self, note_id: str):
        uri = "/api/sns/web/v1/note/like"
        data = {"note_oid": note_id}
        return self.post(uri, data)

    def like_comment(self, note_id: str, comment_id: str):
        uri = "/api/sns/web/v1/comment/like"
        data = {"note_id": note_id, "comment_id": comment_id}
        return self.post(uri, data)

    def dislike_note(self, note_id: str):
        uri = "/api/sns/web/v1/note/dislike"
        data = {"note_oid": note_id}
        return self.post(uri, data)

    def dislike_comment(self, comment_id: str):
        uri = "/api/sns/web/v1/comment/dislike"
        data = {"note_oid": comment_id}
        return self.post(uri, data)

    def get_qrcode(self):
        """create qrcode, you can trasform response url to qrcode

        :return: {"qr_id":"87323168**","code":"280148","url":"xhsdiscover://**","multi_flag":0}
        :rtype: dict
        """
        uri = "/api/sns/web/v1/login/qrcode/create"
        data = {}
        return self.post(uri, data)

    def check_qrcode(self, qr_id: str, code: str):
        uri = "/api/sns/web/v1/login/qrcode/status"
        params = {"qr_id": qr_id, "code": code}
        return self.get(uri, params)

    def activate(self):
        uri = "/api/sns/web/v1/login/activate"
        return self.post(uri, data={})

    def get_user_collect_notes(self, user_id: str, num: int = 30, cursor: str = ""):
        uri = "/api/sns/web/v2/note/collect/page"
        params = {"user_id": user_id, "num": num, "cursor": cursor}
        return self.get(uri, params)

    def get_user_like_notes(self, user_id: str, num: int = 30, cursor: str = ""):
        uri = "/api/sns/web/v1/note/like/page"
        params = {"user_id": user_id, "num": num, "cursor": cursor}
        return self.get(uri, params)

    def get_emojis(self):
        uri = "/api/im/redmoji/detail"
        return self.get(uri)["emoji"]["tabs"][0]["collection"]

    def get_upload_files_permit(self, file_type: str, count: int = 1) -> tuple:
        """获取文件上传的 id

        :param file_type: 文件类型，["images", "video"]
        :param count: 文件数量
        :return:
        """
        uri = "/api/media/v1/upload/web/permit"
        params = {
            "biz_name": "spectrum",
            "scene": file_type,
            "file_count": count,
            "version": "1",
            "source": "web",
        }
        temp_permit = self.get(uri, params)["uploadTempPermits"][0]
        file_id = temp_permit["fileIds"][0]
        token = temp_permit["token"]
        return file_id, token

    def upload_file(
            self,
            file_id: str,
            token: str,
            file_path: str,
            content_type: str = "image/jpeg",
    ):
        """ 将文件上传至指定文件 id 处

        :param file_id: 上传文件 id
        :param token: 上传授权验证 token
        :param file_path: 文件路径，暂只支持本地文件路径
        :param content_type:  【"video/mp4","image/jpeg","image/png"】
        :return:
        """
        url = "https://ros-upload.xiaohongshu.com/" + file_id
        headers = {"X-Cos-Security-Token": token, "Content-Type": content_type}
        with open(file_path, "rb") as f:
            return self.request("PUT", url, data=f, headers=headers)

    def get_suggest_topic(self, keyword=""):
        """通过关键词获取话题信息，发布笔记用

        :param keyword: 话题关键词，如 Python
        :return:
        """
        uri = "/web_api/sns/v1/search/topic"
        data = {
            "keyword": keyword,
            "suggest_topic_request": {"title": "", "desc": ""},
            "page": {"page_size": 20, "page": 1},
        }
        return self.post(uri, data)["topic_info_dtos"]

    def get_suggest_ats(self, keyword=""):
        """通过关键词获取用户信息，发布笔记用

        :param keyword: 用户名关键词，如 ReaJason
        :return:
        """
        uri = "/web_api/sns/v1/search/user_info"
        data = {
            "keyword": keyword,
            "search_id": str(time.time() * 1000),
            "page": {"page_size": 20, "page": 1},
        }
        return self.post(uri, data)["user_info_dtos"]

    def create_note(self, title, desc, note_type, ats: list = None, topics: list = None,
                    image_info: dict = None,
                    video_info: dict = None,
                    post_time: str = None, is_private: bool = False):
        if post_time:
            post_date_time = datetime.strptime(post_time, "%Y-%m-%d %H:%M:%S")
            post_time = round(int(post_date_time.timestamp()) * 1000)
        uri = "/web_api/sns/v2/note"
        business_binds = {
            "version": 1,
            "noteId": 0,
            "noteOrderBind": {},
            "notePostTiming": {
                "postTime": post_time
            },
            "noteCollectionBind": {
                "id": ""
            }
        }

        data = {
            "common": {
                "type": note_type,
                "title": title,
                "note_id": "",
                "desc": desc,
                "source": '{"type":"web","ids":"","extraInfo":"{\\"subType\\":\\"official\\"}"}',
                "business_binds": json.dumps(business_binds, separators=(",", ":")),
                "ats": ats,
                "hash_tag": topics,
                "post_loc": {},
                "privacy_info": {"op_type": 1, "type": int(is_private)},
            },
            "image_info": image_info,
            "video_info": video_info,
        }
        headers = {
            "Referer": "https://creator.xiaohongshu.com/"
        }
        print(data)
        return self.post(uri, data, headers=headers)

    def create_image_note(
            self,
            title,
            desc,
            files: list,
            post_time: str = None,
            ats: list = None,
            topics: list = None,
            is_private: bool = False,
    ):
        """发布图文笔记

        :param title: 笔记标题
        :param desc: 笔记详情
        :param files: 文件路径列表，目前只支持本地路径
        :param post_time: 可选，发布时间，例如 "2023-10-11 12:11:11"
        :param ats: 可选，@用户信息
        :param topics: 可选，话题信息
        :param is_private: 可选，是否私密发布
        :return:
        """
        if ats is None:
            ats = []
        if topics is None:
            topics = []

        images = []
        for file in files:
            image_id, token = self.get_upload_files_permit("image")
            self.upload_file(image_id, token, file)
            images.append(
                {
                    "file_id": image_id,
                    "metadata": {"source": -1},
                    "stickers": {"version": 2, "floating": []},
                    "extra_info_json": '{"mimeType":"image/jpeg"}',
                }
            )
        return self.create_note(title, desc, NoteType.NORMAL.value, ats=ats, topics=topics,
                                image_info={"images": images}, is_private=is_private,
                                post_time=post_time)

    def get_video_first_frame_image_id(self, video_id: str):
        headers = {
            "content-type": "application/json;charset=UTF-8",
            "referer": "https://creator.xiaohongshu.com/",
            "x-sign": "X2d2ea70d804b4f98d20cc70f5643bc26",
        }

        json_data = {"videoId": video_id}

        response = self.__session.post(
            "https://www.xiaohongshu.com/fe_api/burdock/v2/note/query_transcode",
            headers=headers,
            json=json_data,
        )

        res = response.json()
        print(res)
        if res["data"]["hasFirstFrame"]:
            image_id = res["data"]["firstFrameFileId"]
            return image_id
        return None

    def create_video_note(
            self,
            title,
            video_path: str,
            desc: str,
            cover_path: str = None,
            ats: list = None,
            post_time: str = None,
            topics: list = None,
            is_private: bool = False,
            wait_time: int = 3,
    ):
        """发布视频笔记

        :param title: 笔记标题
        :param video_path: 视频文件路径，目前只支持本地路径
        :param desc: 笔记详情
        :param cover_path: 可选，封面文件路径
        :param ats: 可选，@用户信息
        :param post_time: 可选，发布时间
        :param topics: 可选，话题信息
        :param is_private: 可选，是否私密发布
        :param wait_time: 可选，默认 3 s，循环等待获取视频第一帧为笔记封面
        :return:
        :rtype: object
        """
        if ats is None:
            ats = []
        if topics is None:
            topics = []

        file_id, token = self.get_upload_files_permit("video")
        res = self.upload_file(
            file_id,
            token,
            video_path,
            content_type="video/mp4",
        )
        video_id, is_upload = res.headers["X-Ros-Video-Id"], False

        image_id = None
        if cover_path is None:
            for _ in range(10):
                time.sleep(wait_time)
                image_id = self.get_video_first_frame_image_id(video_id)
                if image_id:
                    break

        if cover_path:
            is_upload = True
            image_id, token = self.get_upload_files_permit("image")
            self.upload_file(image_id, token, cover_path)

        cover_info = {
            "file_id": image_id,
            "frame": {"ts": 0, "is_user_select": False, "is_upload": is_upload},
        }

        video_info = {
            "file_id": file_id,
            "timelines": [],
            "cover": cover_info,
            "chapters": [],
            "chapter_sync_text": False,
            "entrance": "web",
        }
        return self.create_note(title, desc, NoteType.VIDEO.value, ats=ats, topics=topics, video_info=video_info,
                                post_time=post_time, is_private=is_private)
