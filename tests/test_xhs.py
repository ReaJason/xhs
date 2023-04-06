import pytest

from xhs import DataFetchError, FeedType, XhsClient


@pytest.fixture
def xhs_client():
    return XhsClient(
        cookie=('webId=e3455f4405340fc431af976dbf3de167;'
                "web_session=040069b253793fdd9ccd9bd21c364b0033a638;"))


def test_init_with_session_id():
    cookie = "123123"
    xhs_client = XhsClient(cookie)
    assert xhs_client.get_cookie() == cookie


def test_get_note_by_id(xhs_client: XhsClient):
    note_id = "63db8819000000001a01ead1"
    data = xhs_client.get_note_by_id(note_id)
    assert data["id"] == note_id


def test_get_self_info(xhs_client: XhsClient):
    data = xhs_client.get_self_info()
    assert isinstance(data, dict)


def test_get_user_info(xhs_client: XhsClient):
    user_id = "5ff0e6410000000001008400"
    data = xhs_client.get_user_info(user_id)
    basic_info = data["basic_info"]
    assert (basic_info["red_id"] == "hh06ovo"
            or basic_info["nickname"] == "小王不爱睡")


def test_get_home_feed(xhs_client: XhsClient):
    recommend_type = FeedType.RECOMMEND
    res = xhs_client.get_home_feed(recommend_type)
    assert len(res["items"]) > 0


def test_get_note_by_keyword(xhs_client: XhsClient):
    keyword = "小红书"
    with pytest.raises(DataFetchError):
        xhs_client.get_note_by_keyword(keyword)


def test_get_user_notes(xhs_client: XhsClient):
    user_id = "63273a77000000002303cc9b"
    data = xhs_client.get_user_notes(user_id)
    assert len(data["notes"]) > 0
