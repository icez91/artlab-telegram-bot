from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboardCategory = [
        [InlineKeyboardButton("➕ Добавить", callback_data="add_category"),
         InlineKeyboardButton("✏️ Обновить", callback_data="update_category"),
         InlineKeyboardButton("❌ Удалить", callback_data="delete_category")],
    ]
    keyboardProduct = [
        [InlineKeyboardButton("➕ Добавить", callback_data="add_product"),
         InlineKeyboardButton("✏️ Обновить", callback_data="update_product"),
         InlineKeyboardButton("❌ Удалить", callback_data="delete_product")]
    ]

    # Сначала выводим категории
    await update.message.reply_text(
        "Привет! Выбери c чем будешь работать\nКатегории товаров:",
        reply_markup=InlineKeyboardMarkup(keyboardCategory)
    )

    # Потом выводим продукты
    await update.message.reply_text(
        "Продукты:",
        reply_markup=InlineKeyboardMarkup(keyboardProduct)
    )
