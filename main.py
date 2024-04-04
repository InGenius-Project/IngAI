import time
from typing import Dict, Generator, List

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from model import Article, ChatModel, MessageModel
from openai_session import OpenAISession

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
ai_session = OpenAISession()


RECORDING_HISTORY: List[MessageModel] = []


def steam_text(input_text: str) -> Generator[str, None, None]:
    text = f"你好嗎, 這是一個測試!!! 這是你的輸入: {input_text}"
    text_stream = text.split()
    RECORDING_HISTORY.append(
        MessageModel(
            role="assistant",
            content=text,
        )
    )
    for text in text_stream:
        time.sleep(0.1)
        yield text


@app.get("/")
def read_root() -> Dict[str, str]:
    return {"Hello": "World"}


@app.post("/analyze")
def analyze(article: Article) -> Dict[str, str]:
    result = ai_session.analyze(article)

    return {
        "is_company_exist": article.facts.is_company_record_gorvernment,
        "average_salary": article.facts.industry_avarage_salary,
        "result": result,
    }


@app.get("/chat_history")
def get_chat_history() -> List[MessageModel]:
    return RECORDING_HISTORY


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        RECORDING_HISTORY.append(MessageModel(role="user", content=data))
        for text in steam_text(data):
            await websocket.send_text(text)


@app.post("/chat")
def chat(chat: ChatModel) -> StreamingResponse:
    # TODO: uncomment this line to burn money
    # return StreamingResponse(
    #     ai_session.chat(MessageModel(role="user", content=chat.text)),
    #     media_type="text/plain",
    # )

    # HACK: this is a hack to simulate the chat
    RECORDING_HISTORY.append(MessageModel(role="user", content=chat.content))
    return StreamingResponse(steam_text(chat.content), media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000)
