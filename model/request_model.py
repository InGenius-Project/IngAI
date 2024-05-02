from enum import Enum
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


class AreaGenType(Enum):
    Resume = 0
    Recruitment = 1


class AreaGenInfo(BaseModel):
    TitleOnly: bool = False
    AreaNum: int = 5
    Title: str = Field(..., case_sensitive=False)
    Areas: list[UserInfoArea]
    Type: AreaGenType

    def to_string(self):
        return f"Title: {self.Title}\n" + "\n".join(
            area.Title + ": " + area.Content for area in self.Areas
        )


class GenerateAreaByTitlePost(BaseModel):
    UserInfo: AreaGenInfo
    AreaTitles: List[str]
