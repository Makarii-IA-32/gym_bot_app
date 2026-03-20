import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from dotenv import load_dotenv
import httpx

# Завантажуємо змінні (Токен)
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")

# Налаштування логування (щоб бачити помилки)
logging.basicConfig(level=logging.INFO)

# Ініціалізація бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обробник команди /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user = message.from_user
    
    # Формуємо дані для відправки на наш API
    user_data = {
        "tg_id": user.id,
        "username": user.username,
        "full_name": user.full_name
    }

    # Відправляємо запит на наш сервер (як ти робив у Swagger)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BACKEND_URL}/users/", json=user_data)
            
            if response.status_code == 200 or response.status_code == 201:
                # Сервер відповів ОК
                await message.answer(f"Привіт, {user.full_name}! 💪\nТи успішно зареєстрований у базі даних.")
            else:
                # Якась помилка
                await message.answer(f"Привіт! Ти вже є в базі, але радий тебе бачити знову.")
                
        except Exception as e:
            await message.answer(f"Виникла помилка з'єднання з сервером: {e}")

# Функція запуску
async def main():
    print("Бот запущено...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())