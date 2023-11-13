# xhs-gpt

Let ChatGPT login, view notes, write and post notes with your Xiaohongshu account.

Build with LangServe and LangChain Expression Language.

## Installation

**Recommend**: Use poetry to manage your venv instead of anaconda or miniconda due to some misunderstanding issues
with `tkinter` and proxies.

First install all requirements for `xhs`, then install `xhs-gpt` in editable mode.

Install `xhs` following the [document](https://reajason.github.io/xhs/basic).
```bash
pip install xhs # 下载 xhs 包

pip install playwright # 下载 playwright

playwright install

docker run -it -d -p 5005:5005 reajason/xhs-api:latest
```

Install `xhs-gpt` in editable mode.

```bash
cd xhs-gpt
# poetry install
pip install -e .  # install xhs-gpt requirements
```

## Launch LangServe

Note that the `login_with_qrcode` agent requires `tkinter`.

Set `OPENAI_API_KEY` (and `HTTP_PROXY`, `HTTPS_PROXY` if you are using a proxy) in your environment variables.

```bash
# cd xhs-gpt
langchain serve
```

Visit playground at http://127.0.0.1:8000/xhs/playground/.