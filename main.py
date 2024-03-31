from typing import Dict

import uvicorn
from fastapi import FastAPI

from model import Article, Facts
from openai_session import OpenAISession
from test_article import TEST_ARTICLE

app = FastAPI()
ai_session = OpenAISession()


@app.get("/")
def read_root() -> Dict[str, str]:
    return {"Hello": "World"}


@app.post("/analyze")
def analyze() -> Dict[str, str]:
    article = Article(
        company_name="台灣積體電路製造股份有限公司",
        facts=Facts(
            industry_avarage_salary="未知",
            is_company_record_gorvernment=False,
        ),
        workType="兼職",
        content=TEST_ARTICLE,
        industry="工業",
    )

    return {"reponse": ai_session.analyze(article)}


@app.post("/chat")
def chat(text: str) -> Dict[str, str]:
    return "ok"


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
