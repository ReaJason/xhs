from enum import Enum
from typing import NamedTuple

from requests import RequestException


class ErrorTuple(NamedTuple):
    code: int
    msg: str


class ErrorEnum(Enum):
    IP_BLOCK = ErrorTuple(300012, "网络连接异常，请检查网络设置或重启试试")
    NOTE_ABNORMAL = ErrorTuple(-510001, "笔记状态异常，请稍后查看")
    NOTE_SECRETE_FAULT = ErrorTuple(-510001, "当前内容无法展示")
    SIGN_FAULT = ErrorTuple(300015, "浏览器异常，请尝试关闭/卸载风险插件或重启试试！")
    SESSION_EXPIRED = ErrorTuple(-100, "登录已过期")


class DataFetchError(RequestException):
    """something error when fetch"""


class IPBlockError(RequestException):
    """fetch so fast that the server block us ip"""


class SignError(RequestException):
    """fetch error because x-s sign verror"""


class NeedVerifyError(RequestException):
    """fetch error because need captcha"""
