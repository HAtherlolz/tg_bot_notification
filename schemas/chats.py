from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class ChatSchema(BaseModel):
    chat_id: Optional[int]
    name: Optional[str]
    created_at: datetime
