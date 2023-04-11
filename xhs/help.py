import hashlib
import json
import random
import time

import requests


def sign(uri, data=None, ctime=None):
    """
    takes in a URI (uniform resource identifier), an optional data dictionary, and an optional ctime parameter. It returns a dictionary containing two keys: "x-s" and "x-t".
    """
    def h(n):
        m = ""
        a = 0
        d = "A4NjFqYu5wPHsO0XTdDgMa2r1ZQocVte9UJBvk6/7=yRnhISGKblCWi+LpfE8xzm3"
        while a < 32:
            o = ord(n[a])
            a += 1
            g = 0
            if a < 32:
                g = ord(n[a])
            a += 1
            h = 0
            if a < 32:
                h = ord(n[a])
            a += 1
            x = ((o & 3) << 4) | (g >> 4)
            p = ((15 & g) << 2) | (h >> 6)
            v = o >> 2
            if h:
                b = h & 63
            else:
                b = 64
            if not g:
                p = b = 64
            m += d[v] + d[x] + d[p] + d[b]
        return m

    v = int(round(time.time() * 1000) if not ctime else ctime)
    raw_str = f"{v}test{uri}{json.dumps(data, separators=(',', ':'), ensure_ascii=False) if isinstance(data, dict) else ''}"
    md5_str = hashlib.md5(raw_str.encode('utf-8')).hexdigest()
    return {
        "x-s": h(md5_str),
        "x-t": str(v),
    }


def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """Converts an integer to a base36 string."""
    if not isinstance(number, int):
        raise TypeError('number must be an integer')

    base36 = ''
    sign = ''

    if number < 0:
        sign = '-'
        number = -number

    if 0 <= number < len(alphabet):
        return sign + alphabet[number]

    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36

    return sign + base36


def base36decode(number):
    return int(number, 36)


def get_search_id():
    e = int(time.time() * 1000) << 64
    t = int(random.uniform(0, 2147483646))
    return base36encode((e + t))


def cookie_str_to_cookie_dict(cookie_str: str):
    cookie_blocks = [cookie_block.split("=")
                     for cookie_block in cookie_str.split(";") if cookie_block]
    return {cookie[0]: cookie[1] for cookie in cookie_blocks}


def cookie_jar_to_cookie_str(session: requests.Session):
    cookie_dict = requests.utils.dict_from_cookiejar(session.cookies)
    return ";".join([f"{key}={value}" for key, value in cookie_dict.items()])


def update_session_cookies_from_cookie(session: requests.Session, cookie: str):
    cookies = session.cookies
    new_cookies = requests.utils.add_dict_to_cookiejar(
        cookies, cookie_str_to_cookie_dict(cookie))
    session.cookies = new_cookies
