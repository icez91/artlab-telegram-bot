from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from bot.handlers.start import start
from bot.handlers.categories import add_category_conv, update_category_conv, delete_category, delete_category_confirm
from bot.handlers.products import (
    add_product_start, add_product_photo, add_product_desc, add_product_price, add_product_category,
    update_product_conv, delete_product_start, delete_product_confirm
)
from bot.core.logger import setup_logger
from bot.utils.constants import BOT_TOKEN

logger = setup_logger()

def main():
    from telegram.ext import MessageHandler, filters, ConversationHandler
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Start
    app.add_handler(CommandHandler("start", start))

    # Categories
    app.add_handler(add_category_conv)
    app.add_handler(update_category_conv)
    app.add_handler(CallbackQueryHandler(delete_category, pattern="delete_category"))
    app.add_handler(CallbackQueryHandler(delete_category_confirm, pattern="delete_.*"))

    # Products
    product_add_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_product_start, pattern="add_product")],
        states={
            0: [MessageHandler(filters.PHOTO, add_product_photo)],
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_desc)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_price)],
            3: [CallbackQueryHandler(add_product_category, pattern="cat_.*")]
        },
        fallbacks=[CommandHandler("cancel", lambda u,c: ConversationHandler.END)],
        per_message=True,
    )
    app.add_handler(product_add_conv)
    app.add_handler(update_product_conv)
    app.add_handler(CallbackQueryHandler(delete_product_start, pattern="delete_product"))
    app.add_handler(CallbackQueryHandler(delete_product_confirm, pattern="delprod_.*"))

    logger.info("Бот запущен!")

    # Запуск polling
    app.run_polling()

if __name__ == "__main__":
    main()
