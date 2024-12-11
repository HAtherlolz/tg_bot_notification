import os

from dotenv import load_dotenv
from pydantic import BaseConfig


load_dotenv()


class Settings(BaseConfig):
    # TG BOT CREDS
    TG_TOKEN: str = os.getenv("TG_TOKEN")
    MONGO_INITDB_ROOT_USERNAME: str = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    MONGO_INITDB_ROOT_PASSWORD: str = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
    # MONGO_INITDB_DATABASE: str = os.getenv("MONGO_INITDB_DATABASE")

    # DATABASE
    # DATABASE_URL: str = f"mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@mongo:27017/"
    DATABASE_URL: str = f"mongodb://mongodb:27017/"

    # REDIS
    REDIS_URL: str = "redis://redis/0"

    # ADMINS GROUP CHAT NAME
    ADMINS_GROUP_CHAT_NAME: str = os.getenv("ADMINS_GROUP_CHAT_NAME")
    
    GROUPS_TO_MONITOR_REACTIONS: list = os.getenv("GROUPS_TO_MONITOR_REACTIONS").split(",")


settings = Settings()
