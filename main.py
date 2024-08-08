from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from cfg.config import settings
from cfg.database import ping_db
from services.bot import Bot
from utils.logs import log


def main():
    ping_db()  # checking if db is running

    log.info("Bot is starting ...")
    app = ApplicationBuilder().token(settings.TG_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", Bot.start))
    app.add_handler(CommandHandler("help", Bot.help_command))
    app.add_handler(CommandHandler("set_moderator", Bot.create_moderator))
    app.add_handler(CommandHandler("get_all_moderators", Bot.moderators_list))

    # Register callback query handler for inline buttons
    app.add_handler(CallbackQueryHandler(Bot.default_buttons))

    # Register message handler for other text messages
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, Bot.handle_message)
    app.add_handler(message_handler)

    log.info("Bot is running and listening")
    app.run_polling()
    log.info("Bot is shut down")


if __name__ == '__main__':
    main()
