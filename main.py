from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, MessageHandler,
    MessageReactionHandler, filters
)

from cfg.config import settings
from cfg.database import ping_db
from services.bot import Bot
from utils.logs import log


def start_bot():
    try:
        app = ApplicationBuilder().token(settings.TG_TOKEN).build()

        app.add_handler(CommandHandler("start", Bot.start))
        app.add_handler(CommandHandler("help", Bot.help_command))
        app.add_handler(CommandHandler("set_moderator", Bot.create_moderator))
        app.add_handler(CommandHandler("get_all_moderators", Bot.moderators_list))
        app.add_handler(CommandHandler("ignore", Bot.ignore))
        app.add_handler(CommandHandler("get_bot_groups", Bot.get_bot_groups))
        app.add_handler(CommandHandler("leave_group", Bot.leave_group_chat))

        message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, Bot.handle_message)
        reactions_handler = MessageReactionHandler(Bot.handle_reaction)
        animations_handler = MessageHandler(filters.ANIMATION, Bot.handle_animation)

        app.add_handler(message_handler)
        app.add_handler(reactions_handler)
        app.add_handler(animations_handler)
        app.add_handler(CallbackQueryHandler(Bot.default_buttons))

        log.info("Bot is running and listening")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except BaseException as e:
        log.info(f"Bot Error: {e}")
        start_bot()


def main():
    ping_db()  # checking if db is running
    log.info("Bot is starting ...")
    start_bot()  # starting bot
    log.info("Bot is shut down")


if __name__ == '__main__':
    main()
