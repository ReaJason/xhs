import datetime

import pytest
import requests

import xhs.help
from xhs import FeedType, IPBlockError, XhsClient
from xhs.exception import DataFetchError

from . import test_cookie
from .utils import beauty_print


@pytest.fixture
def xhs_client():
    def sign(uri, data, a1="", web_session=""):
        res = requests.post("http://localhost:5555/sign",
                            json={"uri": uri, "data": data, "a1": a1, "web_session": web_session})
        signs = res.json()
        return {
            "x-s": signs["x-s"],
            "x-t": signs["x-t"]
        }

    return XhsClient(cookie=test_cookie, sign=sign)


def test_xhs_client_init():
    xhs_client = XhsClient()
    assert xhs_client
    note = xhs_client.get_note_by_id_from_html("646837b9000000001300a4c3")
    beauty_print(note)
    assert note


def test_cookie_setter_getter():
    xhs_client = XhsClient()
    cd = xhs_client.cookie_dict
    beauty_print(cd)
    assert "a1" in cd


def test_external_sign_func():
    def sign(url, data=None, a1="", web_session=""):
        """signature url and data in here"""
        return {}

    with pytest.raises(DataFetchError):
        xhs_client = XhsClient(sign=sign)
        xhs_client.get_qrcode()


def test_get_note_by_id(xhs_client: XhsClient):
    # 13 我是DM发布了一篇小红书笔记，快来看吧！ 😆 F02MULzeoQVJ7YY 😆 http://xhslink.com/GQ0MHB，复制本条信息，打开【小红书】App查看精彩内容！
    note_id = "65682d4500000000380339a5"
    data = xhs_client.get_note_by_id(note_id)
    beauty_print(data)
    assert data["note_id"] == note_id


def test_get_note_by_id_from_html(xhs_client: XhsClient):
    note_id = "65a025ea000000001d03799b"
    data = xhs_client.get_note_by_id_from_html(note_id)
    beauty_print(data)
    print(xhs.help.get_imgs_url_from_note(data))
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


def test_get_user_by_keyword(xhs_client: XhsClient):
    keyword = "Python"
    data = xhs_client.get_user_by_keyword(keyword, page=15)
    # beauty_print(data)
    print(len(data["users"]))
    assert len(data["users"]) > 0


def test_get_user_info(xhs_client: XhsClient):
    user_id = "5ff0e6410000000001008400"
    data = xhs_client.get_user_info(user_id)
    basic_info = data["basic_info"]
    print(datetime.datetime.now())
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


def test_comment_note(xhs_client: XhsClient):
    data = xhs_client.comment_note("65ddbbda000000000700708a", "测试笔记评论功能")
    beauty_print(data)
    comment_id = data["comment"]["id"]
    assert comment_id
    delete_status = xhs_client.delete_note_comment("65ddbbda000000000700708a", comment_id)
    beauty_print(delete_status)
    assert bool(delete_status)


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


def test_get_user_all_notes(xhs_client: XhsClient):
    user_id = "63273a77000000002303cc9b"
    notes = xhs_client.get_user_all_notes(user_id, 0)
    assert len(notes)


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


def test_get_note_all_comments(xhs_client: XhsClient):
    note_id = "658120c0000000000602325f"
    note = xhs_client.get_note_by_id(note_id)
    comments_count = int(note["interact_info"]["comment_count"])
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


def test_get_qrcode_from_creator(xhs_client: XhsClient):
    qrcode = xhs_client.get_qrcode()
    beauty_print(qrcode)


def test_check_qrcode_from_creator(xhs_client: XhsClient):
    creator = xhs_client.check_qrcode_from_creator("682141718111245888")
    beauty_print(creator)


def test_login_from_creator(xhs_client: XhsClient):
    xhs_client.login_from_creator()
    beauty_print(xhs_client.cookie_dict)


def test_get_self_info_from_creator(xhs_client: XhsClient):
    data = xhs_client.get_self_info_from_creator()
    beauty_print(data)


def test_comment_user(xhs_client: XhsClient):
    data = xhs_client.comment_user("65ddbbda000000000700708a",
                                   "65f548eb000000001202e725",  # 回复的评论 ID
                                   "测试回复评论功能")
    beauty_print(data)
    comment_id = data["comment"]["id"]
    assert comment_id
    delete_status = xhs_client.delete_note_comment("65ddbbda000000000700708a", comment_id)
    beauty_print(delete_status)
    assert bool(delete_status)


def test_follow_user(xhs_client: XhsClient):
    follow_status = xhs_client.follow_user("5c3ef37200000000060137dc")
    assert follow_status["fstatus"] == "follows"

    unfollow_status = xhs_client.unfollow_user("5c3ef37200000000060137dc")
    assert unfollow_status["fstatus"] == "none"


def test_collect_note(xhs_client: XhsClient):
    collect_status = xhs_client.collect_note("65ddbbda000000000700708a")
    assert bool(collect_status)
    uncollect_status = xhs_client.uncollect_note("65ddbbda000000000700708a")
    assert bool(uncollect_status)


def test_like_note(xhs_client: XhsClient):
    like_status = xhs_client.like_note("65ddbbda000000000700708a")
    assert bool(like_status)
    unlike_status = xhs_client.dislike_note("65ddbbda000000000700708a")
    assert bool(unlike_status)


def test_like_comment(xhs_client: XhsClient):
    like_status = xhs_client.like_comment("65ddbbda000000000700708a", "65f548eb000000001202e725")
    assert bool(like_status)
    unlike_status = xhs_client.dislike_comment("65ddbbda000000000700708a", "65f548eb000000001202e725")
    assert bool(unlike_status)


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
    xhs_client.save_files_from_note_id(note_id, r"./tests/test_save_files")


def test_get_user_collect_notes(xhs_client: XhsClient):
    notes = xhs_client.get_user_collect_notes(
        user_id="63273a77000000002303cc9b")["notes"]
    beauty_print(notes)
    assert len(notes)


def test_get_user_like_notes(xhs_client: XhsClient):
    notes = xhs_client.get_user_like_notes(
        user_id="63273a77000000002303cc9b")["notes"]
    beauty_print(notes)
    assert len(notes)


@pytest.mark.skip(reason="i don't want to block by ip")
def test_ip_block_error(xhs_client: XhsClient):
    with pytest.raises(IPBlockError):
        note_id = "6413cf6b00000000270115b5"
        for _ in range(150):
            xhs_client.get_note_by_id(note_id)


@pytest.mark.skip(reason="current this func is useless")
def test_activate(xhs_client: XhsClient):
    info = xhs_client.activate()
    beauty_print(info)
    assert info["session"]


def test_get_emojis(xhs_client: XhsClient):
    emojis = xhs_client.get_emojis()
    beauty_print(emojis)
    assert len(emojis)


def test_get_mention_notifications(xhs_client: XhsClient):
    mentions = xhs_client.get_mention_notifications()
    beauty_print(mentions)
    assert len(mentions["message_list"])


def test_get_like_notifications(xhs_client: XhsClient):
    mentions = xhs_client.get_like_notifications()
    beauty_print(mentions)
    assert len(mentions["message_list"])


def test_get_follow_notifications(xhs_client: XhsClient):
    mentions = xhs_client.get_follow_notifications()
    beauty_print(mentions)
    assert len(mentions["message_list"])


def test_get_notes_summary(xhs_client: XhsClient):
    notes = xhs_client.get_notes_summary()
    assert notes


def test_get_notes_statistics(xhs_client: XhsClient):
    notes = xhs_client.get_notes_statistics()
    beauty_print(notes)


def test_get_upload_image_ids(xhs_client: XhsClient):
    image_id, token = xhs_client.get_upload_files_permit("image")
    upload_id = xhs_client.get_upload_id(image_id, token)
    print(upload_id)
    beauty_print(image_id)
    assert image_id


def test_upload_image(xhs_client: XhsClient):
    file_id, file_token = xhs_client.get_upload_files_permit("image")
    file_path = "/Users/reajason/Downloads/wall/wallhaven-x6k21l.png"
    res = xhs_client.upload_file(file_id, file_token, file_path)
    assert res.status_code == 200
    assert res.headers["X-Ros-Preview-Url"]

    with pytest.raises(DataFetchError, match="file already exists"):
        xhs_client.upload_file(file_id, file_token, file_path)


def test_upload_video(xhs_client: XhsClient):
    file_id, file_token = xhs_client.get_upload_files_permit("video")
    file_path = "/Users/reajason/Downloads/1.mp4"
    res = xhs_client.upload_file(file_id, file_token, file_path, content_type="video/mp4")
    assert res.status_code == 200
    assert res.headers["X-Ros-Preview-Url"]


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


@pytest.mark.skip()
def test_create_simple_note(xhs_client: XhsClient):
    title = "我是标题"
    desc = "下面我说两点 \n 1. 第一点 \n 2. 第二点"
    images = [
        "/Users/reajason/Downloads/wall/wallhaven-x6k21l.png",
    ]
    note = xhs_client.create_image_note(title, desc, images, is_private=True, post_time="2023-07-25 23:59:59")
    beauty_print(note)


# @pytest.mark.skip()
def test_create_note_with_ats_topics(xhs_client: XhsClient):
    title = "我是通过自动发布脚本发送的笔记"
    desc = "deployed by GitHub xhs， #Python[话题]# @ReaJason"
    files = [
        "/Users/reajason/ReaJason/wall/1687363223539@0.5x.jpg",
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


@pytest.mark.skip()
def test_create_video_note(xhs_client: XhsClient):
    note = xhs_client.create_video_note(title="123123", desc="测试使用 github.com/reajason/xhs 发布视频笔记",
                                        video_path="/Users/reajason/Downloads/1.mp4",
                                        is_private=True)
    beauty_print(note)


@pytest.mark.skip()
def test_create_video_note_with_cover(xhs_client: XhsClient):
    note = xhs_client.create_video_note(title="123123", video_path="/Users/reajason/Downloads/1.mp4", desc="",
                                        cover_path="/Users/reajason/Downloads/wall/wallhaven-x6k21l.png",
                                        is_private=True)
    beauty_print(note)
