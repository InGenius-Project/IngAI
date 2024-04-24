from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChatRecord(BaseModel):
    id: Optional[int]
    userid: str
    role: str
    content: str
    datetime: datetime
