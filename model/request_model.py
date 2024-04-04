from uuid import UUID

from pydantic import BaseModel


class AnalyzeModel(BaseModel):
    id: UUID
    content: str


class AnalyzeReport(BaseModel):
    id: UUID
    content: str
    result: str


class ChatModel(BaseModel):
    content: str
