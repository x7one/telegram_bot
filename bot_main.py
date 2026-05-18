import asyncio
import os
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")

# Создаём экземпляры бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "👋 Привет! Я бот для поиска информации.\n\n"
        "📝 Используй команду /search никнейм_или_телефон\n\n"
        "🔍 Примеры:\n"
        "/search johndoe\n"
        "/search +79991234567"
    )

# Обработчик команды /search
@dp.message(Command("search"))
async def search_command(message: Message):
    # Получаем текст запроса (удаляем саму команду /search)
    query = message.text.replace("/search", "").strip().lower()

    if not query:
        await message.answer(
            "❌ Введи поисковый запрос!\n"
            "Пример: /search username"
        )
        return

    # Отправляем сообщение о начале поиска
    status_msg = await message.answer(f"🔍 Ищу информацию по запросу: {query}...")

    try:
        # Определяем, похоже ли на телефон
        is_phone_like = bool(re.search(r'[^\da-zA-Z]', query)) or (len(query) >= 10 and query.isdigit())

        # Импортируем функцию поиска (если она у вас есть в отдельном файле)
        # Если нет search_engine.py, замените на свою логику поиска
        try:
            from search_engine import aggregate_search
            results = await aggregate_search(query, is_phone_search=is_phone_like)
        except ImportError:
            # Временно: демо-результаты, если нет search_engine.py
            results = [
                {
                    "source": "Demo Source",
                    "name": "Тестовый пользователь",
                    "handle": f"https://example.com/{query}",
                    "bio": "Это демонстрационный результат поиска"
                }
            ] if query else []

        if results:
            answer = "✅ **Результаты поиска:**\n\n"
            for r in results:
                source_name = r.get("source", "Источник")
                name = r.get("name", "Неизвестно")
                handle = r.get("handle", "")
                bio = r.get("bio", "")

                answer += f"📌 **Источник:** {source_name}\n"
                if name and name != "Unknown" and name != "Неизвестно":
                    answer += f"👤 **Имя:** {name}\n"
                if handle and handle != "Link":
                    answer += f"🔗 **Ссылка:** {handle}\n"
                if bio:
                    answer += f"📝 **О пользователе:** {bio}\n"
                answer += "\n"

            await status_msg.delete()
            await message.answer(answer, parse_mode='Markdown')
        else:
            await status_msg.edit_text(f"❌ Ничего не найдено по запросу: {query}\nПопробуйте другой никнейм или номер телефона.")

    except Exception as e:
        await status_msg.edit_text(f"⚠️ Ошибка при поиске: {str(e)}")

# Обработчик всех остальных сообщений
@dp.message()
async def echo(message: Message):
    await message.answer(
        "🤖 Я понимаю только команды:\n"
        "/start - начать работу\n"
        "/search запрос - найти информацию"
    )

# Запуск бота
async def main():
    print("🚀 Бот запущен и готов к работе!")
    print(f"📡 Подключение к Telegram API...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())