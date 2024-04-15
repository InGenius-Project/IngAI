import asyncio
from typing import Any, AsyncGenerator, Dict, List

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from model import Article, ChatModel, Facts, MessageModel, UserResumeInfo
from service import OpenAISession
from test_article import TEST_ARTICLE

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


# NOTE: Test function
async def steam_text(input_text: str) -> AsyncGenerator[str, None]:
    text = f"你好嗎, 這是一個測試!!! 這是你的輸入: {input_text}\n以下是長輸出測試:\t{TEST_ARTICLE}"
    text_stream = text.split()
    RECORDING_HISTORY.append(
        MessageModel(
            role="assistant",
            content=text,
        )
    )
    for i in text_stream:
        yield i
        await asyncio.sleep(0.1)


@app.get("/")
def read_root() -> Dict[str, str]:
    return {"Hello": "HERE IS AI SERVICE"}


@app.post("/analyze")
def analyze(article: Article) -> Dict[str, Any]:
    article = Article(
        company_name=article.company_name,
        facts=Facts(),
        content=article.content,
        industry=article.industry,
        workType=article.workType,
    )
    result = ai_session.analyze(article)

    return {
        "is_company_exist": article.facts.is_company_record_gorvernment,
        "average_salary": article.facts.industry_avarage_salary,
        "result": result,
    }


@app.post("/chat")
def chat(chat: ChatModel) -> StreamingResponse:
    return StreamingResponse(
        ai_session.chat(MessageModel(role="user", content=chat.content)),
        media_type="text/plain",
    )


@app.post("/generate_area")
def generate_area(user_info: UserResumeInfo) -> StreamingResponse:
    return StreamingResponse(
        ai_session.generate_area(user_info),
        media_type="application/json",
    )


@app.get("/chat_history")
def get_chat_history() -> List[MessageModel]:
    return RECORDING_HISTORY


@DeprecationWarning
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        RECORDING_HISTORY.append(MessageModel(role="user", content=data))

        async for text in steam_text(data):
            message += text
            await websocket.send_text(text)

        RECORDING_HISTORY.append(
            MessageModel(
                role="assistant",
                content=message,
            )
        )


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
