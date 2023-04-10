import pytest

from xhs import FeedType, XhsClient

from .utils import beauty_print


@pytest.fixture
def xhs_client():
    return XhsClient(
        cookie=('webId=e3455f4405340fc431af976dbf3de167;'
                "web_session=040069b253793fdd9ccd9a5f01364b856d4088"))


def test_init_with_session_id():
    cookie = "123123"
    xhs_client = XhsClient(cookie)
    assert xhs_client.get_cookie() == cookie


def test_get_note_by_id(xhs_client: XhsClient):
    note_id = "6413cf6b00000000270115b5"
    data = xhs_client.get_note_by_id(note_id)
    beauty_print(data)
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
