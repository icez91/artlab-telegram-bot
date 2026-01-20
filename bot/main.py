from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from bot.handlers.start import start
from bot.handlers.start import register_handlers
from bot.handlers.categories import add_category_conv
from bot.core.logger import setup_logger
from bot.utils.constants import BOT_TOKEN
from telegram.error import TelegramError
import traceback

logger = setup_logger()

async def error_handler(update, context):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # безопасное сообщение пользователю
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ Произошла ошибка. Попробуйте ещё раз."
            )
    except TelegramError:
        pass


def main():
    from telegram.ext import MessageHandler, filters, ConversationHandler
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    register_handlers(app)

    # -----------------------------
    #           Обработка ошибок
    # -----------------------------
    app.add_error_handler(error_handler)

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
