from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


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
    Title: str = Field(..., case_sensitive=False)
    Content: Optional[str] = Field("無", case_sensitive=False)


class extractionModel(BaseModel):
    content: str


class UserResumeInfo(BaseModel):
    TitleOnly: bool = False
    AreaNum: int = 5
    ResumeTitle: str = Field(..., case_sensitive=False)
    Areas: list[UserInfoArea]

    def to_string(self):
        return f"ResumeTitle: {self.ResumeTitle}\n" + "\n".join(
            area.Title + ": " + area.Content for area in self.Areas
        )


class GenerateAreaByTitlePost(BaseModel):
    UserResumeInfo: UserResumeInfo
    AreaTitles: List[str]
