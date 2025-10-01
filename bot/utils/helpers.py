import os
from telegram import File

async def download_photo(bot, file_id: str, folder="/tmp"):
    """Скачивает фото и возвращает путь к локальному файлу"""
    os.makedirs(folder, exist_ok=True)
    file: File = await bot.get_file(file_id)
    file_path = os.path.join(folder, f"{file_id}.jpg")
    await file.download_to_drive(file_path)
    return file_path
