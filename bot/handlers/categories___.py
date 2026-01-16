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

# Состояния
PHOTO, DESCRIPTION, PARENT, SELECT_CAT = range(4)

# ---------------- ADD CATEGORY ----------------
async def add_category_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Отправть фото для новой категории:")
    return PHOTO

async def add_category_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    context.user_data["photo_file_id"] = photo.file_id
    await update.message.reply_text("✏️ Теперь напиши название и описание категории (в одной строке).")
    return DESCRIPTION

async def add_category_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["description"] = update.message.text
    categories = api.get_categories()
    keyboard = [[InlineKeyboardButton(cat["name"], callback_data=f"parent_{cat['id']}")]
                for cat in categories.get("data", [])]
    keyboard.append([InlineKeyboardButton("➕ Новая категория (parent_id=0)", callback_data="parent_0")])
    await update.message.reply_text("📂 Выбери родительскую категорию:",
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    return PARENT

async def add_category_parent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parent_id = int(query.data.split("_")[1])
    context.user_data["parent_id"] = parent_id

    photo_path = await download_photo(query.bot, context.user_data["photo_file_id"])
    payload = {
        "description": context.user_data["description"],
        "parent_id": context.user_data["parent_id"]
    }
    files = {"photo": open(photo_path, "rb")}
    result = api.add_category(payload, files)
    await query.edit_message_text(f"{'✅ Категория добавлена!' if result.get('statusCode', 200)==200 else '❌ Ошибка: '+str(result)}")
    return ConversationHandler.END

# ---------------- UPDATE CATEGORY ----------------
async def update_category_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = api.get_categories().get("data", [])
    if not categories:
        await update.message.reply_text("❌ Нет категорий для обновления.")
        return ConversationHandler.END
    keyboard = [[InlineKeyboardButton(cat["name"], callback_data=f"update_{cat['id']}")] for cat in categories]
    await update.message.reply_text("✏️ Выбери категорию для обновления:",
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECT_CAT

async def update_category_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat_id = int(query.data.split("_")[1])
    context.user_data["cat_id"] = cat_id
    await query.edit_message_text("📸 Отправь новое фото категории (или /skip, чтобы оставить старое):")
    return PHOTO

async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✏️ Теперь напиши новое описание категории:")
    return DESCRIPTION

async def update_category_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["description"] = update.message.text
    categories = api.get_categories().get("data", [])
    keyboard = [[InlineKeyboardButton(cat["name"], callback_data=f"parent_{cat['id']}")]
                for cat in categories]
    keyboard.append([InlineKeyboardButton("➕ Новая категория (parent_id=0)", callback_data="parent_0")])
    await update.message.reply_text("📂 Выбери родительскую категорию:",
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    return PARENT

async def update_category_parent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parent_id = int(query.data.split("_")[1])
    context.user_data["parent_id"] = parent_id
    cat_id = context.user_data["cat_id"]
    payload = {"description": context.user_data["description"], "parent_id": parent_id}
    files = None
    if "photo_file_id" in context.user_data:
        photo_path = await download_photo(query.bot, context.user_data["photo_file_id"])
        files = {"photo": open(photo_path, "rb")}
    result = api.update_category(cat_id, payload, files)
    await query.edit_message_text(f"{'✅ Категория обновлена!' if result.get('statusCode',200)==200 else '❌ Ошибка: '+str(result)}")
    return ConversationHandler.END

# ---------------- DELETE CATEGORY ----------------
async def delete_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = api.get_categories().get("data", [])
    if not categories:
        await update.message.reply_text("❌ Нет категорий для удаления.")
        return
    keyboard = [[InlineKeyboardButton(cat["name"], callback_data=f"delete_{cat['id']}")] for cat in categories]
    await update.message.reply_text("❌ Выбери категорию для удаления:",
                                    reply_markup=InlineKeyboardMarkup(keyboard))

async def delete_category_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat_id = int(query.data.split("_")[1])
    result = api.delete_category(cat_id)
    await query.edit_message_text(f"{'✅ Категория удалена!' if result.get('statusCode',200)==200 else '❌ Ошибка: '+str(result)}")

# ---------------- CONVERSATION HANDLERS ----------------
from telegram.ext import ConversationHandler, CommandHandler

add_category_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_category_start, pattern="add_category")],
    states={
        PHOTO: [MessageHandler(filters.PHOTO, add_category_photo)],
        DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_category_description)],
        PARENT: [CallbackQueryHandler(add_category_parent, pattern="parent_.*")]
    },
    fallbacks=[CommandHandler("cancel", lambda u,c: ConversationHandler.END)],
)

update_category_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(update_category_start, pattern="update_category")],
    states={
        SELECT_CAT: [CallbackQueryHandler(update_category_select, pattern="update_.*")],
        PHOTO: [MessageHandler(filters.PHOTO, add_category_photo),
                CommandHandler("skip", skip_photo)],
        DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_category_description)],
        PARENT: [CallbackQueryHandler(update_category_parent, pattern="parent_.*")]
    },
    fallbacks=[CommandHandler("cancel", lambda u,c: ConversationHandler.END)],
)
