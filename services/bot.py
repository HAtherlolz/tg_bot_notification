from typing import List
from zoneinfo import ZoneInfo
from datetime import datetime

from telegram import Bot as TGBot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackContext

from utils.logs import log
from cfg.config import settings

from schemas.users import UserSchema
from schemas.igonred_users import IgnoredUserSchema

from repositories.mongodb import (
    ChatRepository, MessageRepository,
    MessageSchema, ChatSchema, UserRepository,
    IgnoredUserRepository, MessageSchemaUpdate
)


class Bot:
    @classmethod
    async def handle_message(
            cls,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        if not update.message:
            return

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
    async def handle_reaction(
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        utc_date_time = update.message.date if hasattr(update.message, 'date') else None
        if not utc_date_time:
            utc_date_time = datetime.now()
        gmt_plus_3 = ZoneInfo('Etc/GMT-3')  # 'Etc/GMT-3' corresponds to GMT+3
        local_date_time = utc_date_time.astimezone(gmt_plus_3)
        
        chat_id = update.message_reaction.chat.id
        chat_name = update.message_reaction.chat.title
        message_id = update.message_reaction.message_id
        first_name = update.message_reaction.user.first_name
        last_name = update.message_reaction.user.last_name
        username = update.message_reaction.user.username
        new_reactions = update.message_reaction.new_reaction
        log.info(f"Chat ID: {chat_id}, type : {type(chat_id)}")
        log.info(f"Message ID: {message_id}, type : {type(message_id)}")
        log.info(f"First Name: {first_name}, last name: {last_name}")
        log.info(f"User: {username}, type : {type(username)}")
        log.info(f"New Reactions: {new_reactions}, type : {type(new_reactions)}")
        # TODO: afted testing delete all above
        # message = MessageSchemaUpdate(
        #     # message_id=message_id,
        #     chat_id=chat_id,
        #     name=update.message_reaction.chat.title,
        #     username=username,
        # )
        
        # log.info(f"GROUPS_TO_MONITOR_REACTIONS: {settings.GROUPS_TO_MONITOR_REACTIONS}")
        # if update.message_reaction.chat.title in settings.GROUPS_TO_MONITOR_REACTIONS:
        #     log.info(f"Message is in the list of groups to monitor reactions")
        #     try:
        #         log.info(f"Trying to mark message as notified after reaction")
        #         MessageRepository.mark_msg_as_notified(message)
        #     except Exception as e:
        #         log.info(f"Error while marking message as notified: {e}")
        if first_name is None:
            first_name = ""
        if last_name is None:
            last_name = ""

        if "stark" in first_name.lower() or "stark" in last_name.lower():
            msg: MessageSchema = MessageSchema(
                chat_id=chat_id, name=chat_name,
                message="REACTION", username=username,
                created_at=local_date_time, first_name=first_name,
                last_name=last_name
            )
            MessageRepository.create_msg(msg)
    
    @staticmethod
    async def handle_animation(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        log.info("ANIMATION HANDLER")
        
        utc_date_time = update.message.date if hasattr(update.message, 'date') else None
        if not utc_date_time:
            utc_date_time = datetime.now()
        gmt_plus_3 = ZoneInfo('Etc/GMT-3')  # 'Etc/GMT-3' corresponds to GMT+3
        local_date_time = utc_date_time.astimezone(gmt_plus_3)
        
        chat_id = update.message.chat.id
        chat_name = update.message.chat.title
        username = update.effective_sender.username
        first_name = update.effective_sender.first_name
        last_name = update.effective_sender.last_name
        msg: MessageSchema = MessageSchema(
            chat_id=chat_id, name=chat_name,
            message="GIF", username=username,
            created_at=local_date_time, first_name=first_name,
            last_name=last_name
        )
        animation = update.message.animation.file_name
        log.info(f"Message: {animation}, type : {type(animation)}")
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
            [InlineKeyboardButton("Get all groups where bot is", callback_data='get_bot_groups')],
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
        elif query.data == 'get_bot_groups':
            await Bot.get_bot_groups(query, context)

    @staticmethod
    async def help_command(update: Update, context: CallbackContext) -> None:
        await update.message.reply_text(
            "Here are the available commands:\n"
            "/start - Start the bot\n"
            "/help - Show help message\n"
            "/set_moderator - Make me a moderator\n"
            "/get_all_moderators - Get all moderators\n"
            "/ignore {username you want to ignore} - Set user's username to ignore for notification list\n"
            "/get_bot_groups - Get all groups bot in\n"
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

    @staticmethod
    async def ignore(
            update: Update,
            context: CallbackContext
    ) -> None:

        if not update.message:
            return

        command = update.message.text
        msg: List[str] = command.split(" ")
        if len(msg) != 2:
            await update.message.reply_text(f"The command is incorrect \n"
                                            f"Correct from is - /ignore 'username'")
            return

        username: str = command.split(" ")[1]
        if "@" in username:
            user: IgnoredUserSchema = IgnoredUserSchema(username=username[1:])
        else:
            user: IgnoredUserSchema = IgnoredUserSchema(username=username)

        res: bool = IgnoredUserRepository.set_ignored_user(user)
        log.info(f"Does the user with username {user.username} added to ignore: {res}")

        if res:
            res_msg: str = f"The messages from {user.username} will " \
                           f"be ignored, and won't notify"
        else:
            res_msg: str = f"The user with username {user.username} " \
                           f"is already in ignore list"

        await update.message.reply_text(res_msg)

    @classmethod
    async def get_bot_groups(cls, update: Update, context: CallbackContext) -> None:
        """Command to retrieve all group chats the bot is in."""
        group_chats = ChatRepository.get_all_group_chats()
        
        log.info(f"Group chats: {group_chats}")
        
        if not group_chats:
            await update.message.reply_text(
                "I am not in any group chats!"
            )
            return

        group_list = "\n".join([chat.name for chat in group_chats])

        # Create a formatted list of groups
        await update.message.reply_text(
            f"Here are the groups I am in:\n\n{group_list}\n"
        )
    
    @staticmethod
    async def leave_group_chat(update: Update, context: CallbackContext) -> None:
        """Command to remove the bot from the current group chat."""
        chat = ChatRepository.get_group_chat_by_name(update.message.text.split(" ", 1)[1])
        await update._bot.leave_chat(chat_id=chat.chat_id)
        # log.info(f"Bot has left the group: {update.effective_chat.title} (ID: {chat_id})")
        await update.message.reply_text(
            f"Bot has left the group: {update.message.text.split(' ', 1)[1]}!"
        )
