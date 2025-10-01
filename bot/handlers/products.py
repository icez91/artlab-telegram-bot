from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters
)
from bot.core.api import APIClient
from bot.utils.helpers import download_photo

api = APIClient()

# Состояния для ConversationHandler
PRODUCT_PHOTO, PRODUCT_DESC, PRODUCT_PRICE, PRODUCT_CATEGORY, PRODUCT_SELECT = range(5)

# -----------------------
# --- Add Product ---
# -----------------------
async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь фото товара:")
    return PRODUCT_PHOTO

async def add_product_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.photo[-1].file_id
    path = await download_photo(update.message.bot, file_id)
    context.user_data["product_photo"] = path
    await update.message.reply_text("Отправь описание товара:")
    return PRODUCT_DESC

async def add_product_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["product_desc"] = update.message.text
    await update.message.reply_text("Отправь цену товара:")
    return PRODUCT_PRICE

async def add_product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["product_price"] = update.message.text
    # Выбор категории
    cats = api.get_categories().get("response", [])
    keyboard = [[InlineKeyboardButton(c["name"], callback_data=str(c["id"]))] for c in cats]
    await update.message.reply_text("Выбери категорию товара:", reply_markup=InlineKeyboardMarkup(keyboard))
    return PRODUCT_CATEGORY

async def add_product_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat_id = int(update.callback_query.data)
    files = {"image": open(context.user_data["product_photo"], "rb")}
    data = {
        "description": context.user_data["product_desc"],
        "price": context.user_data["product_price"],
        "category_id": cat_id
    }
    res = api.add_product(data=data, files=files)
    await update.callback_query.message.reply_text(f"Товар добавлен: {res.get('message')}")
    return ConversationHandler.END

add_product_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_product_start, pattern="add_product")],
    states={
        PRODUCT_PHOTO: [MessageHandler(filters.PHOTO, add_product_photo)],
        PRODUCT_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_desc)],
        PRODUCT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_price)],
        PRODUCT_CATEGORY: [CallbackQueryHandler(add_product_category)],
    },
    fallbacks=[]
)

# -----------------------
# --- Update Product ---
# -----------------------
async def update_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prods = api.get_products().get("response", [])
    if not prods:
        await update.callback_query.message.reply_text("Нет товаров для обновления.")
        return ConversationHandler.END
    keyboard = [[InlineKeyboardButton(p["description"], callback_data=str(p["id"]))] for p in prods]
    await update.callback_query.message.reply_text("Выбери товар для обновления:", reply_markup=InlineKeyboardMarkup(keyboard))
    return PRODUCT_SELECT

async def update_product_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prod_id = int(update.callback_query.data)
    context.user_data["prod_id"] = prod_id
    await update.callback_query.message.reply_text("Отправь новое фото товара (или пропусти /skip):")
    return PRODUCT_PHOTO

async def update_product_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.photo[-1].file_id
    path = await download_photo(update.message.bot, file_id)
    context.user_data["product_photo"] = path
    await update.message.reply_text("Отправь новое описание товара:")
    return PRODUCT_DESC

async def skip_product_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пропущено. Отправь новое описание товара:")
    return PRODUCT_DESC

async def update_product_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["product_desc"] = update.message.text
    await update.message.reply_text("Отправь новую цену товара:")
    return PRODUCT_PRICE

async def update_product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["product_price"] = update.message.text
    cats = api.get_categories().get("response", [])
    keyboard = [[InlineKeyboardButton(c["name"], callback_data=str(c["id"]))] for c in cats]
    await update.message.reply_text("Выбери новую категорию товара:", reply_markup=InlineKeyboardMarkup(keyboard))
    return PRODUCT_CATEGORY

async def update_product_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat_id = int(update.callback_query.data)
    prod_id = context.user_data["prod_id"]
    data = {
        "description": context.user_data["product_desc"],
        "price": context.user_data["product_price"],
        "category_id": cat_id
    }
    files = None
    if "product_photo" in context.user_data:
        files = {"image": open(context.user_data["product_photo"], "rb")}
    res = api.update_product(prod_id, data=data, files=files)
    await update.callback_query.message.reply_text(f"Товар обновлён: {res.get('message')}")
    return ConversationHandler.END

update_product_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(update_product_start, pattern="update_product")],
    states={
        PRODUCT_SELECT: [CallbackQueryHandler(update_product_select)],
        PRODUCT_PHOTO: [MessageHandler(filters.PHOTO, update_product_photo),
                        CommandHandler("skip", skip_product_photo)],
        PRODUCT_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_product_desc)],
        PRODUCT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_product_price)],
        PRODUCT_CATEGORY: [CallbackQueryHandler(update_product_category)]
    },
    fallbacks=[]
)

# -----------------------
# --- Delete Product ---
# -----------------------
async def delete_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prods = api.get_products().get("response", [])
    if not prods:
        await update.callback_query.message.reply_text("Нет товаров для удаления.")
        return ConversationHandler.END
    keyboard = [[InlineKeyboardButton(p["description"], callback_data=str(p["id"]))] for p in prods]
    await update.callback_query.message.reply_text("Выбери товар для удаления:", reply_markup=InlineKeyboardMarkup(keyboard))
    return PRODUCT_SELECT

async def delete_product_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prod_id = int(update.callback_query.data)
    res = api.delete_product(prod_id)
    await update.callback_query.message.reply_text(f"Товар удалён: {res.get('message')}")
    return ConversationHandler.END

delete_product_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(delete_product_start, pattern="delete_product")],
    states={
        PRODUCT_SELECT: [CallbackQueryHandler(delete_product_confirm)]
    },
    fallbacks=[]
)
