import asyncio
import aiohttp
import os
import re

class SearchEngine:
    def __init__(self):
        # Глобальный токен для поиска по телефону (пример)
        self.phone_api_token = os.getenv("PHONE_DB_API_KEY", "7b4abcbde4fc7322e8ab134fa0d90691")

    async def search_github(self, username: str):
        """Парсинг GitHub"""
        # URL для GitHub API
        url = f"https://api.github.com/users/{username}"
        headers = {}
        # Если есть токен, добавляем его в заголовки
        # headers["Authorization"] = f"token {os.getenv('GITHUB_TOKEN', '')}" # Раскомментируй, если настроишь токен

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
                        # Простая проверка, что страница открылась (без сложных парсинга)
                        return {
                            "source": "VKontakte",
                            "handle": f"vk.com/{query}",
                            "name": f"Пользователь {query}",
                            "avatar": "https://sun9-67.userapi.com/...", # Можно заменить на реальное фото
                            "bio": f"Найден в VK по адресу: {url}"
                        }
        except:
            pass
        return None

    async def search_phone(self, phone: str):
        """Поиск по номеру телефона (через пример API)"""
        if not self.phone_api_token:
            return None

        # Пример API (заглушка)
        return {
            "source": "Phone DB (Example)",
            "name": f"Человек с номером {phone}",
            "handle": phone,
            "avatar": "https://example.com/avatar.png"
        }

    async def aggregate_search(self, query: str, is_phone: bool = False):
        """
        Основная функция поиска.
        Аргументы:
        - query: сам текст запроса (ник или телефон)
        - is_phone: флаг, нужно ли искать по телефону
        """
        engine = SearchEngine()
        results = []

        if is_phone:
            # Если флаг is_phone=True, ищем только по телефону
            phone_res = await engine.search_phone(query)
            if phone_res:
                results.append(phone_res)
        else:
            # Если флаг is_phone=False, ищем по сайтам (GitHub, VK)
            # И стараемся распознать телефон по формату
            github_res = await engine.search_github(query)
            if github_res:
                results.append(github_res)

            vk_res = await engine.search_vk(query)
            if vk_res:
                results.append(vk_res)

            # Дополнительно: если в запросе есть цифры и длина > 7, проверяем и по телефону (как "бонус")
            if any(c.isdigit() for c in query) and len(query) > 7:
                phone_res = await engine.search_phone(query)
                if phone_res:

                    results.append(phone_res)

        return results