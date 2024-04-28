import asyncio
from typing import Annotated, Any, AsyncGenerator, Dict, Generator, List

import uvicorn
from fastapi import Depends, FastAPI, Request, WebSocket
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from icecream import ic

from model import (
    Article,
    ChatModel,
    FactsModel,
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
chat_service_dep = Annotated[dict, Depends(ChatService)]


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
    user_id: str, stream: Generator[str, None, None], chat_service: ChatService
):
    global USER_MESSAGE_RECORD
    if USER_MESSAGE_RECORD.get(user_id) is None:
        USER_MESSAGE_RECORD[user_id] = ""

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
def analyze(article: Article) -> JSONResponse:
    article.Facts = FactsModel()

    return {
        "IsCompanyExist": article.Facts.is_company_record_gorvernment,
        "AverageSalary": article.Facts.industry_avarage_salary,
        "Content": "該徵才文章的信息缺乏透明度，並未提及工作時間、薪酬等重要細節，這本身就是一大紅旗。根據所提供的事實，任何在台灣合法運營的職位應明確遵守勞工正常工作時間規定（每日不超過8小時，每週不超過40小時）並提供不低於基本工資（月薪新臺幣27470元或時薪新臺幣183元）。此外，該公司未在政府資料庫中登記，這是一個顯著的警告信號，表明其可能不遵守國家的工作法規或潛在地從事非法活動。該職位要求結合了C# UI/UX開發技能與農場作業，這種技能組合相當不尋常，可能暗示著不實或誇大的職位描述，進一步增加了該職位是詐騙的可能性。总的来说，缺乏關鍵信息和公司未正式登記的事實，加上職位描述中的不合理要求，都指向該徵才廣告極有可能是詐騙。",
    }

    ic(article)
    result = ai_session.analyze(article)

    return {
        "IsCompanyExist": article.Facts.is_company_record_gorvernment,
        "AverageSalary": article.Facts.industry_avarage_salary,
        "Content": result,
    }


@app.post("/chat")
def chat(
    chat: ChatModel, user_id: str, chat_service: chat_service_dep
) -> StreamingResponse:
    user_message = MessageModel(role="user", content=chat.content)
    ai_response = read_chat_response(
        user_id, ai_session.chat(user_message), chat_service
    )
    chat_service.push_chat(user_id, user_message)
    return StreamingResponse(
        ai_response,
        media_type="text/plain",
    )


@app.post("/generate_area")
def generate_area(req: UserResumeInfo) -> JSONResponse:
    return ic(ai_session.generate_area(req))


@app.post("/generate_area_by_title")
def generate_area_by_title(req: GenerateAreaByTitlePost) -> JSONResponse:
    return ic(ai_session.generate_area_by_title(req.UserResumeInfo, req.AreaTitles))


@app.post("/keywords_extraction")
def keyword_extraction(text_input: extractionModel) -> list[str]:
    keywords = ai_session.extraction(content=text_input.content)
    return ic(keywords)


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
