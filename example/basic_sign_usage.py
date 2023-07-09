import requests

from xhs import XhsClient


def sign(uri, data=None, a1="", web_session=""):
    # 填写自己的 flask 签名服务端口地址
    res = requests.post("http://localhost:5005",
                        json={"uri": uri, "data": data, "a1": a1, "web_session": web_session})
    signs = res.json()
    return {
        "x-s": signs["x-s"],
        "x-t": signs["x-t"]
    }


if __name__ == '__main__':
    cookie = "please get cookie from your website"
    xhs_client = XhsClient(cookie, sign=sign)
    # get note info
    note_info = xhs_client.get_note_by_id("63db8819000000001a01ead1")
    print(note_info)
