from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    filters
)
import httpx
import io
from PIL import Image
from bot.api_client import APIClient

# ---- Стадии ----
ADD_CATEGORY_NAME = 1
ADD_CATEGORY_DESCRIPTION = 2
ADD_CATEGORY_PHOTO = 3

# ---- Старт добавления категории ----
async def add_category_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text("Введите название новой категории:")
    return ADD_CATEGORY_NAME


# ---- Получаем название категории ----
async def add_category_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["category_name"] = update.message.text.strip()

    await update.message.reply_text("Введите описание категории:")
    return ADD_CATEGORY_DESCRIPTION


# ---- Получаем описание категории ----
async def add_category_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["category_description"] = update.message.text.strip()

    await update.message.reply_text("Отправьте фото категории или отправьте /skip:")
    return ADD_CATEGORY_PHOTO


# ---- Получаем фото и конвертируем в JPEG ----
async def add_category_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()

    img_bytes = io.BytesIO()
    await file.download_to_memory(out=img_bytes)
    img_bytes.seek(0)

    # ---- Конвертация в JPEG ----
    img = Image.open(img_bytes).convert("RGB")
    jpeg_bytes = io.BytesIO()
    img.save(jpeg_bytes, format="JPEG")
    jpeg_bytes.seek(0)

    context.user_data["category_photo"] = jpeg_bytes

    return await send_category_to_api(update, context)


# ---- Пропуск фото ----
async def skip_category_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["category_photo"] = None
    return await send_category_to_api(update, context)


# ---- Отправляем категорию на API ----
async def send_category_to_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("category_name")
    description = context.user_data.get("category_description")
    photo_bytes = context.user_data.get("category_photo")
    user_id = update.effective_user.id

    data = {
        "name": name,
        "description": description,
    }

    files = {}
    if photo_bytes:
        files["image"] = ("category.jpg", photo_bytes, "image/jpeg")

    api = APIClient(user_id)
    response = await api.add_category(data, files)
    if not response.get("success", False):
        await update.message.reply_text(f"❌{response.message}")
        return ConversationHandler.END

    await update.message.reply_text(f"✅ Категория «{name}» успешно создана!")
    return ConversationHandler.END


# ---- Отмена ----
async def add_category_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END


# ---- ConversationHandler ----
add_category_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(add_category_start, pattern="^add_category$")
    ],
    states={
        ADD_CATEGORY_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_category_name)
        ],
        ADD_CATEGORY_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_category_description)
        ],
        ADD_CATEGORY_PHOTO: [
            MessageHandler(filters.PHOTO, add_category_photo),
            CommandHandler("skip", skip_category_photo)
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex("^(отмена|cancel)$"), add_category_cancel)
    ],
    per_chat=True,
)
