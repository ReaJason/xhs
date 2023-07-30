import time
from time import sleep

import pytest
import requests
from playwright.sync_api import sync_playwright

from xhs import FeedType, IPBlockError, XhsClient
from xhs.exception import SignError, DataFetchError
from . import test_cookie
from .utils import beauty_print


def get_context_page(playwright):
    chromium = playwright.chromium
    browser = chromium.launch(headless=True)
    browser_context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )
    browser_context.add_init_script(path="/Users/reajason/ReaJason/xhs/tests/stealth.min.js")
    context_page = browser_context.new_page()
    return browser_context, context_page


playwright = sync_playwright().start()
browser_context, context_page = get_context_page(playwright)


@pytest.fixture
def xhs_client():
    def sign(uri, data, a1="", web_session=""):
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

    return XhsClient(cookie=test_cookie, sign=sign)


# def test_xhs_client_init():
#     xhs_client = XhsClient()
#     assert xhs_client


# def test_cookie_setter_getter():
#     xhs_client = XhsClient()
#     cd = xhs_client.cookie_dict
#     beauty_print(cd)
#     assert "web_session" in cd


def test_external_sign_func():
    def sign(url, data=None, a1=""):
        """signature url and data in here"""
        return {}

    with pytest.raises(SignError):
        xhs_client = XhsClient(sign=sign)
        xhs_client.get_qrcode()


def test_get_note_by_id(xhs_client: XhsClient):
    note_id = "6413cf6b00000000270115b5"
    data = xhs_client.get_note_by_id(note_id)
    beauty_print(data)
    assert data["note_id"] == note_id


def test_get_note_by_id_from_html(xhs_client: XhsClient):
    note_id = "6413cf6b00000000270115b5"
    data = xhs_client.get_note_by_id_from_html(note_id)
    beauty_print(data)
    assert data["note_id"] == note_id


def test_report_note_metrics(xhs_client: XhsClient):
    res = xhs_client.report_note_metrics(
        note_id="646837b9000000001300a4c3",
        note_type=1,
        note_user_id="6037a89b0000000001007e72",
        viewer_user_id="63273a77000000002303cc9b")
    beauty_print(res)
    assert res["success"]


def test_get_self_info(xhs_client: XhsClient):
    data = xhs_client.get_self_info()
    beauty_print(data)
    assert isinstance(data, dict)


def test_get_self_info2(xhs_client: XhsClient):
    data = xhs_client.get_self_info2()
    beauty_print(data)
    assert isinstance(data, dict)


def test_get_user_info(xhs_client: XhsClient):
    user_id = "5ff0e6410000000001008400"
    data = xhs_client.get_user_info(user_id)
    basic_info = data["basic_info"]
    beauty_print(data)
    assert (basic_info["red_id"] == "hh06ovo"
            or basic_info["nickname"] == "小王不爱睡")


def test_get_home_feed_category(xhs_client: XhsClient):
    data = xhs_client.get_home_feed_category()
    beauty_print(data)
    assert len(data)


def test_get_home_feed(xhs_client: XhsClient):
    recommend_type = FeedType.RECOMMEND
    data = xhs_client.get_home_feed(recommend_type)
    beauty_print(data)
    assert len(data["items"]) > 0


def test_get_search_suggestion(xhs_client: XhsClient):
    res = xhs_client.get_search_suggestion("jvm")
    beauty_print(res)
    assert len(res)


def test_get_note_by_keyword(xhs_client: XhsClient):
    keyword = "小红书"
    data = xhs_client.get_note_by_keyword(keyword)
    beauty_print(data)
    assert len(data["items"]) > 0


def test_get_user_notes(xhs_client: XhsClient):
    user_id = "63273a77000000002303cc9b"
    data = xhs_client.get_user_notes(user_id)
    beauty_print(data)
    assert len(data["notes"]) > 0


# @pytest.mark.skip(reason="it take much request and time")
def test_get_user_all_notes(xhs_client: XhsClient):
    user_id = "576e7b1d50c4b4045222de08"
    notes = xhs_client.get_user_all_notes(user_id, 0)
    beauty_print(notes)


def test_get_note_comments(xhs_client: XhsClient):
    note_id = "63db8819000000001a01ead1"
    comments = xhs_client.get_note_comments(note_id)
    beauty_print(comments)
    assert len(comments["comments"]) > 0


def test_get_note_sub_comments(xhs_client: XhsClient):
    note_id = "63db8819000000001a01ead1"
    root_comment_id = "63db8957000000001c03e5b5"
    comments = xhs_client.get_note_sub_comments(note_id, root_comment_id)
    beauty_print(comments)
    assert len(comments["comments"]) > 0


@pytest.mark.skip(reason="it take much request and time")
def test_get_note_all_comments(xhs_client: XhsClient):
    note_id = "63db8819000000001a01ead1"
    note = xhs_client.get_note_by_id(note_id)
    comments_count = int(note["interact_info"]["comment_count"])
    print(comments_count)
    comments = xhs_client.get_note_all_comments(note_id)
    beauty_print(comments)
    assert len(comments) == comments_count


def test_get_qrcode(xhs_client: XhsClient):
    data = xhs_client.get_qrcode()
    beauty_print(data)
    assert data["url"].startswith("xhsdiscover://")


def test_check_qrcode(xhs_client: XhsClient):
    qrcode = xhs_client.get_qrcode()
    data = xhs_client.check_qrcode(qr_id=qrcode["qr_id"], code=qrcode["code"])
    beauty_print(data)
    assert "code_status" in data


@pytest.mark.skip()
def test_comment_note(xhs_client: XhsClient):
    data = xhs_client.comment_note("642b96640000000014027cd2", "你最好说你在说你自己")
    beauty_print(data)
    assert data["comment"]["id"]


@pytest.mark.skip()
def test_comment_user(xhs_client: XhsClient):
    data = xhs_client.comment_user("642b96640000000014027cd2",
                                   "642f801000000000150037f8",
                                   "我评论你了")
    beauty_print(data)
    assert data["comment"]["id"]


@pytest.mark.skip()
def test_delete_comment(xhs_client: XhsClient):
    data = xhs_client.delete_note_comment("642b96640000000014027cd2",
                                          "642f801000000000150037f8")
    beauty_print(data)


@pytest.mark.parametrize("note_id", [
    "6413cf6b00000000270115b5",
    "641718a200000000130143f2"
])
@pytest.mark.skip()
def test_save_files_from_note_id(xhs_client: XhsClient, note_id: str):
    xhs_client.save_files_from_note_id(note_id, r"C:\Users\ReaJason\Desktop")


@pytest.mark.parametrize("note_id", [
    "639a7064000000001f0098a8",
    "635d06790000000015020497"
])
@pytest.mark.skip()
def test_save_files_from_note_id_invalid_title(xhs_client: XhsClient, note_id):
    xhs_client.save_files_from_note_id(note_id, r"C:\Users\ReaJason\Desktop")


@pytest.mark.skip()
def test_get_user_collect_notes(xhs_client: XhsClient):
    notes = xhs_client.get_user_collect_notes(
        user_id="63273a77000000002303cc9b")["notes"]
    beauty_print(notes)
    assert len(notes) == 1


@pytest.mark.skip()
def test_get_user_like_notes(xhs_client: XhsClient):
    notes = xhs_client.get_user_like_notes(
        user_id="63273a77000000002303cc9b")["notes"]
    beauty_print(notes)
    assert len(notes) == 2


@pytest.mark.skip(reason="i don't want to block by ip")
def test_ip_block_error(xhs_client: XhsClient):
    with pytest.raises(IPBlockError):
        note_id = "6413cf6b00000000270115b5"
        for _ in range(150):
            xhs_client.get_note_by_id(note_id)


def test_activate(xhs_client: XhsClient):
    info = xhs_client.activate()
    beauty_print(info)
    assert info["session"]


def test_get_emojis(xhs_client: XhsClient):
    emojis = xhs_client.get_emojis()
    beauty_print(emojis)
    assert len(emojis)


def test_get_upload_image_ids(xhs_client: XhsClient):
    count = 5
    ids = xhs_client.get_upload_image_ids(count)
    beauty_print(ids)
    assert len(ids[0]["fileIds"]) == count


def test_upload_image(xhs_client: XhsClient):
    ids = xhs_client.get_upload_image_ids(1)
    file_info = ids[0]
    file_id = file_info["fileIds"][0]
    file_token = file_info["token"]
    file_path = "/Users/reajason/Downloads/4538306CF3BDC215721FCC0532AF4D3D.jpg"
    res = xhs_client.upload_image(file_id, file_token, file_path)
    assert res.status_code == 200
    print(res.headers["X-Ros-Preview-Url"])

    with pytest.raises(DataFetchError, match="file already exists"):
        xhs_client.upload_image(file_id, file_token, file_path)


def test_get_suggest_topic(xhs_client: XhsClient):
    topic_keyword = "Python"
    topics = xhs_client.get_suggest_topic(topic_keyword)
    beauty_print(topics)
    assert topic_keyword.upper() in topics[0]["name"].upper()


def test_get_suggest_ats(xhs_client: XhsClient):
    ats_keyword = "星空的花"
    ats = xhs_client.get_suggest_ats(ats_keyword)
    beauty_print(ats)
    assert ats_keyword.upper() in ats[0]["user_base_dto"]["user_nickname"].upper()


def test_create_simple_note(xhs_client: XhsClient):
    title = "我是标题"
    desc = "下面我说两点 \n 1. 第一点 \n 2. 第二点"
    images = [
        "/Users/reajason/Downloads/221686462282_.pic.png",
    ]
    note = xhs_client.create_image_note(title, desc, images, is_private=True, post_time="2023-07-25 23:59:59")
    beauty_print(note)


def test_create_note_with_ats_topics(xhs_client: XhsClient):
    title = "我是通过自动发布脚本发送的笔记"
    desc = "deployed by GitHub xhs， #Python[话题]# @ReaJason"
    files = [
        "/Users/reajason/Downloads/221686462282_.pic.png",
    ]

    # 可以通过 xhs_client.get_suggest_ats(ats_keyword) 接口获取用户数据
    ats = [
        {"nickname": "ReaJason", "user_id": "63273a77000000002303cc9b", "name": "ReaJason"}
    ]

    # 可以通过 xhs_client.get_suggest_topic(topic_keyword) 接口获取标签数据
    topics = [
        {
            "id": "5d35dd9b000000000e0088dc", "name": "Python", "type": "topic",
            "link": "https://www.xiaohongshu.com/page/topics/5d35dd9ba059940001703e38?naviHidden=yes"
        }
    ]
    note = xhs_client.create_image_note(title, desc, files, ats=ats, topics=topics, is_private=True,
                                        post_time="2023-07-25 23:59:59")
    beauty_print(note)


def test_create_video_note(xhs_client: XhsClient):
    note = xhs_client.create_video_note(title="123123", video_path="/Users/reajason/Downloads/2.mp4", desc="",
                                        is_private=True)
    beauty_print(note)


def test_create_video_note_with_cover(xhs_client: XhsClient):
    note = xhs_client.create_video_note(title="123123", video_path="/Users/reajason/Downloads/2.mp4", desc="",
                                        cover_path="/Users/reajason/Downloads/221686462282_.pic.jpg",
                                        is_private=True)
    beauty_print(note)
