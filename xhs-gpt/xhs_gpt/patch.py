from typing import Union, Dict, Tuple


def patch_langchain():
    """Allow multi-input tools."""
    import langchain.tools.base

    def new_to_args_and_kwargs(self, tool_input: Union[str, Dict]) -> Tuple[Tuple, Dict]:
        """Convert tool input to pydantic model."""
        args, kwargs = super(langchain.tools.base.Tool, self)._to_args_and_kwargs(tool_input)
        # Remove backwards compatibility.
        all_args = list(args) + list(kwargs.values())
        return tuple(all_args), {}

    # Monkey patch the Tool class
    langchain.tools.base.Tool._to_args_and_kwargs = new_to_args_and_kwargs


def patch_xhs():
    """Login to Xiaohongshu should default to bypass proxies."""
    import xhs
    old = xhs.core.XhsClient

    class XhsClient(old):

        def __init__(self, cookie=None, user_agent=None, timeout=10, proxies=None, sign=None):
            super().__init__(cookie=cookie, user_agent=user_agent, timeout=timeout,
                             proxies=proxies if proxies else {"http_proxy": None, "https_proxy": None}, sign=sign)

    xhs.core.XhsClient = XhsClient
