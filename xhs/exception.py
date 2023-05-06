from requests import RequestException


class DataFetchError(RequestException):
    """something error when fetch"""


class IPBlockError(RequestException):
    """fetch so fast that the server block us ip"""
