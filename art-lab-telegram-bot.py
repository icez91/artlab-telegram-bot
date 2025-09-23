import json
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)

# ------------------------
# Загрузка конфига
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

BOT_TOKEN = config["BOT_TOKEN"]
API_URL = config["API_URL"]

logging.basicConfig(level=logging.INFO)

# ------------------------
# Состояния ConversationHandler
ADD_CATEGORY_DESC, ADD_CATEGORY_IMAGE, ADD_PRODUCT_DESC, ADD_PRODUCT_PRICE, ADD_PRODUCT_CATEGORY, ADD_PRODUCT_IMAGE = range(6)

# ------------------------
# Функция обработки ответа API
def handle_api_response(resp):
    try:
        data = resp.json()
        if resp.status_code >= 400:
            msg = f"❌ Ошибка API {data.get('statusCode', resp.status_code)}: {data.get('message', 'Unknown error')}"
            details = data.get("details")
            if details:
                msg += f"\nДетали: {details}"
            return False, msg
        return True, data
    except json.JSONDecodeError:
        return False, f"❌ Ошибка: невозможно разобрать ответ API ({resp.text})"

# ------------------------
# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category")],
        [InlineKeyboardButton("➕ Добавить товар", callback_data="add_product")]
    ]
    await update.message.reply_text(
        "Привет! Выбери действие:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ------------------------
# Добавление категории
async def add_category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Введите описание категории:")
    return ADD_CATEGORY_DESC

async def add_category_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cat_desc"] = update.message.text
    await update.message.reply_text("Загрузите картинку категории:")
    return ADD_CATEGORY_IMAGE

async def add_category_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("❌ Пожалуйста, отправьте фото категории.")
        return ADD_CATEGORY_IMAGE

    photo = await update.message.photo[-1].get_file()
    file_path = f"category_{update.message.from_user.id}.jpg"
    await photo.download_to_drive(file_path)

    files = {"image": open(file_path, "rb")}
    data = {"description": context.user_data["cat_desc"]}
    try:
        resp = requests.post(f"{API_URL}/categories", data=data, files=files)
        success, msg = handle_api_response(resp)
        await update.message.reply_text(msg if not success else "✅ Категория добавлена на backend!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка запроса: {e}")

    return ConversationHandler.END

# ------------------------
# Добавление товара
async def add_product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Введите описание товара:")
    return ADD_PRODUCT_DESC

async def add_product_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["prod_desc"] = update.message.text
    await update.message.reply_text("Введите цену товара (только число):")
    return ADD_PRODUCT_PRICE

async def add_product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price_text = update.message.text.replace(",", ".")
    try:
        price = float(price_text)
        context.user_data["prod_price"] = str(price)
        # Получаем категории с backend
        try:
            resp = requests.get(f"{API_URL}/categories")
            success, data = handle_api_response(resp)
            if not success:
                await update.message.reply_text(data)
                return ConversationHandler.END
            categories = data.get("response", []) or data
            if not categories:
                await update.message.reply_text("❌ Нет категорий для выбора. Сначала добавьте категорию.")
                return ConversationHandler.END
            # Inline кнопки категорий
            buttons = [[InlineKeyboardButton(c.get("description","Без названия"), callback_data=str(c["id"]))] for c in categories]
            keyboard = InlineKeyboardMarkup(buttons)
            await update.message.reply_text("Выберите категорию:", reply_markup=keyboard)
            return ADD_PRODUCT_CATEGORY
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка запроса категорий: {e}")
            return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("❌ Цена должна быть числом. Попробуйте ещё раз:")
        return ADD_PRODUCT_PRICE

# Выбор категории
async def add_product_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["prod_category_id"] = query.data
    await query.edit_message_text("Теперь загрузите фото товара:")
    return ADD_PRODUCT_IMAGE

# Загрузка фото и отправка товара на backend
async def add_product_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("❌ Пожалуйста, отправьте фото товара.")
        return ADD_PRODUCT_IMAGE

    photo = await update.message.photo[-1].get_file()
    file_path = f"product_{update.message.from_user.id}.jpg"
    await photo.download_to_drive(file_path)

    files = {"image": open(file_path, "rb")}
    data = {
        "description": context.user_data["prod_desc"],
        "price": context.user_data["prod_price"],
        "category_id": context.user_data["prod_category_id"]
    }
    try:
        resp = requests.post(f"{API_URL}/products", data=data, files=files)
        success, msg = handle_api_response(resp)
        await update.message.reply_text(msg if not success else "✅ Товар добавлен на backend!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка запроса: {e}")

    return ConversationHandler.END

# ------------------------
# Основной запуск
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_category_callback, pattern="add_category"),
            CallbackQueryHandler(add_product_callback, pattern="add_product")
        ],
        states={
            ADD_CATEGORY_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_category_desc)],
            ADD_CATEGORY_IMAGE: [MessageHandler(filters.PHOTO, add_category_image)],

            ADD_PRODUCT_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_desc)],
            ADD_PRODUCT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_price)],
            ADD_PRODUCT_CATEGORY: [CallbackQueryHandler(add_product_category)],
            ADD_PRODUCT_IMAGE: [MessageHandler(filters.PHOTO, add_product_image)],
        },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    app.run_polling()

if __name__ == "__main__":
    main()
