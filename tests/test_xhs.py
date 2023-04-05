from xhs import XhsClient


def test_init_with_session_id():
    session_id = "123123"
    xhsClient = XhsClient(session_id)
    assert xhsClient.get_session_id() == session_id


def test_init_with_options():
    pass
