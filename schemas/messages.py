from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class MessageSchema(BaseModel):
    chat_id: Optional[int]
    name: Optional[str]
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    message: Optional[str]
    username: Optional[str]
    created_at: datetime
    is_notified: bool = False
