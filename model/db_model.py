from datetime import datetime

from pydantic import BaseModel


class ChatRecord(BaseModel):
    id: int | None
    userid: str
    role: str
    content: str
    datetime: datetime
