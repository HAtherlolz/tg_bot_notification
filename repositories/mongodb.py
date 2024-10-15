from typing import List, Dict
from datetime import datetime

from pymongo.collection import Collection

from schemas.chats import ChatSchema
from schemas.users import UserSchema
from schemas.messages import MessageSchema
from schemas.igonred_users import IgnoredUserSchema

from cfg.config import settings
from cfg.database import msg_db, chat_db, user_db, ignored_user_db

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
    
    @classmethod
    def get_group_chat_by_name(cls, chat_name: str) -> Dict:
        chat = cls.db.find_one({"name": chat_name})
        return ChatSchema(**chat)


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
    def get_last_message_from_all_group_chats_for_today(cls) -> List[MessageSchema]:
        last_msgs = []
        group_chats = ChatRepository.get_all_group_chats()

        # Get the current date at midnight
        today_start = datetime.combine(datetime.today(), datetime.min.time())

        for chat in group_chats:
            last_msg = cls.db.find_one(
                {
                    "chat_id": chat.chat_id,
                    "created_at": {"$gte": today_start}
                },
                sort=[("created_at", -1)])
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


class IgnoredUserRepository:
    db: Collection = ignored_user_db

    @classmethod
    def set_ignored_user(
            cls,
            user: IgnoredUserSchema
    ) -> bool:
        ignored_user = cls.db.find({"username": user.username})
        if list(ignored_user):
            return False

        cls.db.insert_one(user.dict())
        return True

    @classmethod
    def get_list_ignored_users(cls) -> List[IgnoredUserSchema]:
        ignored_user = cls.db.find()
        return [IgnoredUserSchema(**ign_usr) for ign_usr in ignored_user]

