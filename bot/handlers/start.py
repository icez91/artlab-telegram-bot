from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
)
from bot.core.api import APIClient

# ----------------------------------------------------------
#           Старт: проверка пользователя
# ----------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    tg_user_id = update.effective_user.id
    api = APIClient(tg_user_id)
    data = {
        "telegram_id": tg_user_id,
    }
    res = await api.check_user(data)

    if not res.get("response", {}).get("authorized", False):
        await update.message.reply_text("⛔ У вас нет доступа!\nОбратитесь к администратору.")
        return

    # ---- Пользователь авторизован — выводим главное меню ----
    keyboard_main = [
        [InlineKeyboardButton("📂 Категории", callback_data="menu_categories")],
        [InlineKeyboardButton("📦 Продукты", callback_data="menu_products")],
    ]

    await update.message.reply_text(
        "Выберите с чем будете работать:",
        reply_markup=InlineKeyboardMarkup(keyboard_main)
    )


# ----------------------------------------------------------
#           Меню категорий
# ----------------------------------------------------------
async def menu_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("➕ Добавить", callback_data="add_category"),
            InlineKeyboardButton("✏️ Обновить", callback_data="update_category"),
            InlineKeyboardButton("❌ Удалить", callback_data="delete_category"),
        ]
    ]

    await query.edit_message_text(
        "Категории:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ----------------------------------------------------------
#           Меню продуктов
# ----------------------------------------------------------
async def menu_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("➕ Добавить", callback_data="add_product"),
            InlineKeyboardButton("✏️ Обновить", callback_data="update_product"),
            InlineKeyboardButton("❌ Удалить", callback_data="delete_product"),
        ]
    ]

    await query.edit_message_text(
        "Продукты:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ----------------------------------------------------------
#           Регистрация обработчиков
# ----------------------------------------------------------
def register_handlers(application):
    application.add_handler(CallbackQueryHandler(menu_categories, pattern="^menu_categories$"))
    application.add_handler(CallbackQueryHandler(menu_products, pattern="^menu_products$"))
