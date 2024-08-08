import os

from dotenv import load_dotenv
from pydantic import BaseConfig


load_dotenv()


class Settings(BaseConfig):
    # TG BOT CREDS
    TG_TOKEN: str = os.getenv("TG_TOKEN")

    # DATABASE
    DATABASE_URL: str = "mongodb://mongo:27017/"

    # REDIS
    REDIS_URL: str = "redis://redis/0"

    # ADMINS GROUP CHAT NAME
    ADMINS_GROUP_CHAT_NAME: str = os.getenv("ADMINS_GROUP_CHAT_NAME")


settings = Settings()
