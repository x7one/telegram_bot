import asyncio
import aiohttp
import os
import re

# Глобальный класс или набор функций
class SearchEngine:
    def __init__(self):
        # Используем токен из .env или дефолтный
        self.phone_api_token = os.getenv("PHONE_DB_API_KEY", "7b4abcbde4fc7322e8ab134fa0d90691")

    async def search_github(self, username: str):
        """Парсинг GitHub"""
        url = f"https://api.github.com/users/{username}"
        headers = {}
        # Если хочешь добавить токен GitHub:
        # if os.getenv('GITHUB_TOKEN'):
        #     headers["Authorization"] = f"token {os.getenv('GITHUB_TOKEN')}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "source": "GitHub",
                            "name": data.get("name"),
                            "handle": f"github.com/{data.get('login')}",
                            "avatar": data.get("avatar_url"),
                            "bio": data.get("bio")
                        }
                    elif response.status == 404:
                        return None
        except:
            pass
        return None

    async def search_vk(self, query: str):
        """Поиск по VK"""
        url = f"https://www.vk.com/{query}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        return {
                            "source": "VKontakte",
                            "handle": f"vk.com/{query}",
                            "name": f"Пользователь {query}",
                            "avatar": "https://sun9-67.userapi.com/...",
                            "bio": f"Найден в VK по адресу: {url}"
                        }
        except:
            pass
        return None

    async def search_phone(self, phone: str):
        """Поиск по номеру телефона"""
        if not self.phone_api_token:
            return None
        return {
            "source": "Phone DB",
            "name": f"Человек с номером {phone}",
            "handle": phone,
            "avatar": "https://example.com/avatar.png"
        }

# --- Глобальная функция (То, что ищет бот) ---
# Мы создаем её отдельно от класса, чтобы import работал корректно
async def aggregate_search(query: str, is_phone: bool = False):
    """
    Главная функция поиска.
    is_phone=True -> ищем по телефону
    is_phone=False -> ищем по сайтам (GitHub/VK)
    """
    engine = SearchEngine()
    results = []

    if is_phone:
        # Если явно просили телефон, ищем только там
        phone_res = await engine.search_phone(query)
        if phone_res:
            results.append(phone_res)
    else:
        # Иначе ищем по соцсетям
        github_res = await engine.search_github(query)
        if github_res:
            results.append(github_res)

        vk_res = await engine.search_vk(query)
        if vk_res:
            results.append(vk_res)

        # Дополнительная проверка на телефон (если в запросе цифры)
        if any(c.isdigit() for c in query) and len(query) > 7:
            phone_res = await engine.search_phone(query)
            if phone_res:
                results.append(phone_res)

    return results