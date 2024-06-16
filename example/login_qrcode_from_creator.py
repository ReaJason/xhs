import datetime
import json
from time import sleep

import qrcode
import requests

from xhs import XhsClient


def sign(uri, data=None, a1="", web_session=""):
    # 填写自己的 flask 签名服务端口地址
    res = requests.post("http://localhost:5555/sign",
                        json={"uri": uri, "data": data, "a1": a1, "web_session": web_session})
    signs = res.json()
    return {
        "x-s": signs["x-s"],
        "x-t": signs["x-t"]
    }


# pip install qrcode
if __name__ == '__main__':
    xhs_client = XhsClient(sign=sign)
    print(datetime.datetime.now())
    qr_res = xhs_client.get_qrcode_from_creator()
    qr_id = qr_res["id"]
    qr = qrcode.QRCode(version=1, error_correction=qrcode.ERROR_CORRECT_L,
                       box_size=50,
                       border=1)
    qr.add_data(qr_res["url"])
    qr.make()
    qr.print_ascii()

    while True:
        check_qrcode = xhs_client.check_qrcode_from_creator(qr_id)
        print(check_qrcode)
        sleep(1)
        if check_qrcode["status"] == 1:
            ticket = check_qrcode["ticket"]
            xhs_client.customer_login(ticket)
            xhs_client.login_from_creator()
            break

    print(json.dumps(xhs_client.get_self_info_from_creator(), ensure_ascii=False, indent=4))
