import asyncio
from typing import Any, AsyncGenerator, Dict, Generator, List

import uvicorn
from fastapi import Depends, FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from model import (
    Article,
    ChatModel,
    Facts,
    GenerateAreaByTitlePost,
    MessageModel,
    UserResumeInfo,
    extractionModel,
)
from service import ChatService, OpenAISession
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

RECORDING_HISTORY: List[str] = []
USER_MESSAGE_RECORD: Dict[str, str] = {}


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


def read_chat_response(
    user_id: str,
    stream: Generator[str, None, None],
    chat_service: ChatService = Depends(ChatService),
):
    global USER_MESSAGE_RECORD
    if USER_MESSAGE_RECORD.get(user_id) is None:
        USER_MESSAGE_RECORD.append(user_id, "")

    for i in stream:
        USER_MESSAGE_RECORD[user_id] += i
        yield i

    ai_message = MessageModel(
        role="assistant", content=USER_MESSAGE_RECORD.get(user_id)
    )
    chat_service.push_chat(user_id, ai_message)


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
def chat(
    chat: ChatModel, user_id: int, chat_service: ChatService = Depends(ChatService)
) -> StreamingResponse:
    user_message = MessageModel(role="user", content=chat.content)
    ai_response = ai_session.chat(user_message)
    chat_service.push_chat(user_id, user_message)
    return StreamingResponse(
        ai_response,
        media_type="text/plain",
    )


@app.post("/generate_area")
def generate_area(req: UserResumeInfo) -> str:
    return ai_session.generate_area(req)


@app.post("/generate_area_by_title")
def generate_area_by_title(req: GenerateAreaByTitlePost) -> str:
    return ai_session.generate_area_by_title(req.UserResumeInfo, req.AreaTitles)


@app.post("/keywords_extraction")
def keyword_extraction(text_input: extractionModel) -> list[str]:
    keywords = ai_session.extraction(content=text_input.content)
    print(keywords)
    return keywords


@app.get("/chat_history")
def get_chat_history(
    user_id: str, chat_service: ChatService = Depends(ChatService)
) -> List[MessageModel]:
    return chat_service.get_user_chat(user_id)


@DeprecationWarning
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        RECORDING_HISTORY.append(MessageModel(role="user", content=data))
        message = ""
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
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000)
