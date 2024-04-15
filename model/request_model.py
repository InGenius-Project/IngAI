from typing import Optional
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


class UserInfoArea(BaseModel):
    title: str
    content: Optional[str] = "無"


class UserResumeInfo(BaseModel):
    resume_title: str
    areas: list[UserInfoArea]

    def to_string(self):
        return f"ResumeTitle: {self.resume_title}\n" + "\n".join(
            area.title + ": " + area.content for area in self.areas
        )
