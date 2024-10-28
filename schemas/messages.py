from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class MessageSchema(BaseModel):
    # TODO: add message_id
    chat_id: Optional[int]
    name: Optional[str]
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    message: Optional[str]
    username: Optional[str]
    created_at: datetime
    is_notified: bool = False


class MessageSchemaUpdate(BaseModel):
    # TODO: add message_id
    chat_id: Optional[int] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    message: Optional[str] = None
    username: Optional[str] = None
    created_at: Optional[datetime] = None
    is_notified: Optional[bool] = None