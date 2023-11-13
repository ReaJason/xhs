from fastapi import FastAPI
from langserve import add_routes

from xhs_gpt.agents import xhs_agent_executor, get_feed_agent_executor, get_note_agent_executor, \
    create_note_agent_executor, login_with_phone_agent_executor, \
    login_with_qrcode_agent_executor

app = FastAPI()

add_routes(app, xhs_agent_executor, path='/xhs')
add_routes(app, get_feed_agent_executor, path='/xhs/feed')
add_routes(app, get_note_agent_executor, path='/xhs/note')
add_routes(app, create_note_agent_executor, path='/xhs/create_note')
add_routes(app, login_with_phone_agent_executor, path='/xhs/login_with_phone')
add_routes(app, login_with_qrcode_agent_executor, path='/xhs/login_with_qrcode')

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
