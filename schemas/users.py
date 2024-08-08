from typing import Optional

from pydantic import BaseModel


class UserSchema(BaseModel):
    username: Optional[str]
    chat_id: Optional[int]
    is_moderator: bool
    receive_notifications: bool
