from typing import List

from pymongo.collection import Collection

from schemas.chats import ChatSchema
from schemas.messages import MessageSchema
from schemas.users import UserSchema

from cfg.config import settings
from cfg.database import msg_db, chat_db, user_db

from utils.logs import log


class ChatRepository:
    db: Collection = chat_db

    @classmethod
    def get_chats_by_id(cls, chat_id: int) -> List[ChatSchema]:
        chats = cls.db.find({"chat_id": chat_id})
        return [ChatSchema(**chat) for chat in chats]

    @classmethod
    def create_chat(cls, chat: ChatSchema) -> bool:
        chats = cls.get_chats_by_id(chat.chat_id)
        if chats:
            return False

        if chat.chat_id < 0:  # Group chats have negative ids
            cls.db.insert_one(chat.dict())
            return True

        return False

    @classmethod
    def get_all_group_chats(cls) -> List[ChatSchema]:
        chats = cls.db.find({"chat_id": {"$lt": 0}})
        return [ChatSchema(**chat) for chat in chats]

    @classmethod
    def get_admins_chat_id(cls) -> int:
        log.info(f"ADMINS_GROUP_CHAT_NAME: {settings.ADMINS_GROUP_CHAT_NAME}")
        chat = cls.db.find_one({"name": settings.ADMINS_GROUP_CHAT_NAME})
        log.info(f"CHAT: {chat}")
        if not chat:
            return 0

        return chat.get("chat_id")


class MessageRepository:
    db: Collection = msg_db

    @classmethod
    def get_msgs_by_id(cls, chat_id: int) -> List[MessageSchema]:
        msgs = cls.db.find({"chat_id": chat_id})
        return [MessageSchema(**msg) for msg in msgs]

    @classmethod
    def create_msg(cls, msg: MessageSchema) -> bool:
        cls.db.insert_one(msg.dict())
        return True

    @classmethod
    def get_last_message_from_all_group_chats(cls) -> List[MessageSchema]:
        last_msgs = []
        group_chats = ChatRepository.get_all_group_chats()
        for chat in group_chats:
            last_msg = cls.db.find_one({"chat_id": chat.chat_id}, sort=[("created_at", -1)])
            if last_msg:
                last_msgs.append(MessageSchema(**last_msg))
        return last_msgs

    @classmethod
    def mark_msg_as_notified(cls, msg: MessageSchema) -> None:
        cls.db.update_one(
            {"chat_id": msg.chat_id, "created_at": msg.created_at},
            {"$set": {"is_notified": True}}
        )


class UserRepository:
    db: Collection = user_db

    @classmethod
    def create_user(cls, user: UserSchema) -> bool:
        users = list(cls.db.find({"username": user.username}))
        if users:
            return False

        cls.db.insert_one(user.dict())
        return True

    @classmethod
    def get_user_by_username(cls, username: str) -> UserSchema:
        user = cls.db.find_one({"username": username})
        return UserSchema(**user)

    @classmethod
    def get_all_moderators(cls) -> List[UserSchema]:
        users = cls.db.find({"is_moderator": True})
        return [UserSchema(**user) for user in users]

    @classmethod
    def set_notifications(cls, username: str, receive_notifications: bool) -> bool:
        user = cls.db.find({"username": username})
        if user:
            cls.db.update_one({"username": username}, {"$set": {"receive_notifications": receive_notifications}})
            return True
        return False
