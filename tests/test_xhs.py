import pytest
import requests

from xhs import FeedType, IPBlockError, XhsClient

from . import test_cookie
from .utils import beauty_print


@pytest.fixture
def xhs_client():
    return XhsClient(cookie=test_cookie)


def test_xhs_client_init():
    xhs_client = XhsClient()
    assert xhs_client


def test_cookie_setter_getter():
    xhs_client = XhsClient()
    cd = requests.utils.dict_from_cookiejar(xhs_client.session.cookies)
    beauty_print(cd)
    assert "web_session" in cd


def test_get_note_by_id(xhs_client: XhsClient):
    note_id = "6413cf6b00000000270115b5"
    data = xhs_client.get_note_by_id(note_id)
    beauty_print(data)
    assert data["note_id"] == note_id


def test_get_note_by_id_from_html(xhs_client: XhsClient):
    note_id = "6413cf6b00000000270115b5"
    data = xhs_client.get_note_by_id_from_html(note_id)
    # pre_data = xhs_client.get_note_by_id(note_id)
    beauty_print(data)
    # assert pre_data == data
    assert data["note_id"] == note_id


def test_get_self_info(xhs_client: XhsClient):
    data = xhs_client.get_self_info()
    beauty_print(data)
    assert isinstance(data, dict)


def test_get_user_info(xhs_client: XhsClient):
    user_id = "5ff0e6410000000001008400"
    data = xhs_client.get_user_info(user_id)
    basic_info = data["basic_info"]
    beauty_print(data)
    assert (basic_info["red_id"] == "hh06ovo"
            or basic_info["nickname"] == "小王不爱睡")


def test_get_home_feed(xhs_client: XhsClient):
    recommend_type = FeedType.RECOMMEND
    data = xhs_client.get_home_feed(recommend_type)
    beauty_print(data)
    assert len(data["items"]) > 0


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


@pytest.mark.skip(reason="it take much request and time")
def test_get_user_all_notes(xhs_client: XhsClient):
    user_id = "63273a77000000002303cc9b"
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


@pytest.mark.skip()
def test_check_qrcode(xhs_client: XhsClient):
    data = xhs_client.check_qrcode("901061680834121471", "658742")
    assert data.get("code_status")


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
