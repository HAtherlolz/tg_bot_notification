from pymongo import MongoClient

from cfg.config import settings
from utils.logs import log


db_url = settings.DATABASE_URL
client = MongoClient('mongodb://mongo:27017/')
db = client["DB"]
msg_db = db["messages"]
chat_db = db["chats"]
user_db = db["users"]
ignored_user_db = db["ignored_users"]


def ping_db():
    """ Check db connection """
    try:
        client.admin.command("ping")
        log.info("Connected to database")
    except Exception as e:
        log.info("Error database connection. ", e)
