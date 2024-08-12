from zoneinfo import ZoneInfo
from datetime import datetime

from telegram import Bot as TGBot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackContext

from utils.logs import log
from cfg.config import settings

from schemas.users import UserSchema
from repositories.mongodb import (
    ChatRepository, MessageRepository,
    MessageSchema, ChatSchema, UserRepository
)


class Bot:
    @classmethod
    async def handle_message(
            cls,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
    ) -> None:

        utc_date_time = update.message.date if hasattr(update.message, 'date') else None
        if not utc_date_time:
            utc_date_time = datetime.now()

        gmt_plus_3 = ZoneInfo('Etc/GMT-3')  # 'Etc/GMT-3' corresponds to GMT+3
        local_date_time = utc_date_time.astimezone(gmt_plus_3)

        chat_id = update.message.chat.id
        chat_name = update.message.chat.title
        message_text = update.message.text
        username = update.message.from_user.username
        first_name = getattr(update.message.from_user, 'first_name', None)
        last_name = getattr(update.message.from_user, 'last_name', None)

        log.info(f"Chat ID: {chat_id}, type : {type(chat_id)}")  # Optional[int]
        log.info(f"Chat Name: {chat_name}, type : {type(chat_name)}")  # Optional[str]
        log.info(f"Message: {message_text}, type : {type(message_text)}")  # Optional[str]
        log.info(f"Username: {username} ,type :{type(username)}")  # Optional[str]

        msg: MessageSchema = MessageSchema(
            chat_id=chat_id, name=chat_name,
            message=message_text, username=username,
            created_at=local_date_time, first_name=first_name,
            last_name=last_name
        )

        chat: ChatSchema = ChatSchema(
            chat_id=chat_id, name=chat_name,
            created_at=local_date_time
        )

        ChatRepository.create_chat(chat)
        if msg.name != settings.ADMINS_GROUP_CHAT_NAME:
            MessageRepository.create_msg(msg)

    @staticmethod
    async def send_message_to_chat(chat_id: int, message: str) -> None:
        bot = TGBot(token=settings.TG_TOKEN)
        await bot.send_message(chat_id=chat_id, text=message)

    # ============== Command handlers ===============
    @staticmethod
    async def start(update: Update, context: CallbackContext) -> None:
        keyboard = [
            [InlineKeyboardButton("Help", callback_data='help')],
            [InlineKeyboardButton("I am a moderator", callback_data='set_moderator')],
            [InlineKeyboardButton("Get all moderators", callback_data='get_all_moderators')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Hello! I am your bot. How can I assist you today?', reply_markup=reply_markup)

    @staticmethod
    async def default_buttons(update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        await query.answer()
        if query.data == 'help':
            await Bot.help_command(query, context)
        elif query.data == 'set_moderator':
            await Bot.create_moderator(query, context)
        elif query.data == 'get_all_moderators':
            await Bot.moderators_list(query, context)

    @staticmethod
    async def help_command(update: Update, context: CallbackContext) -> None:
        await update.message.reply_text(
            "Here are the available commands:\n"
            "/start - Start the bot\n"
            "/help - Show help message\n"
            "/set_moderator - Make me a moderator\n"
            "/get_all_moderators - Get all moderators"
        )

    @staticmethod
    async def create_moderator(update: Update, context: CallbackContext) -> None:
        user: UserSchema = UserSchema(
            username=update.from_user.username,
            chat_id=update.message.chat.id,
            is_moderator=True,
            receive_notifications=True
        )
        UserRepository.create_user(user)
        await update.message.reply_text('You are a moderator now!')

    @staticmethod
    async def moderators_list(update: Update, context: CallbackContext) -> None:
        moderators = UserRepository.get_all_moderators()
        moderators_list = "\n".join([f"@{mod.username}" for mod in moderators])
        await update.message.reply_text(f"Moderators:\n{moderators_list}")
