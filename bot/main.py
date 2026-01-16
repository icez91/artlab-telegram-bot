from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from bot.handlers.start import start
from bot.handlers.categories import add_category_conv
from bot.core.logger import setup_logger
from bot.utils.constants import BOT_TOKEN

logger = setup_logger()

def main():
    from telegram.ext import MessageHandler, filters, ConversationHandler
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # -----------------------------
    #           Старт
    # -----------------------------
    app.add_handler(CommandHandler("start", start))

    # -----------------------------
    #           Категории
    # -----------------------------
    app.add_handler(add_category_conv)

    logger.info("Бот запущен!")

    # -----------------------------
    #           Старт polling
    # -----------------------------
    app.run_polling()

if __name__ == "__main__":
    main()
