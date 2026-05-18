import asyncio
import aiohttp
import os
import re

class SearchEngine:
    def __init__(self):
        # self.github_token = os.getenv("GITHUB_TOKEN")
        self.phone_api_token = os.getenv("7b4abcbde4fc7322e8ab134fa0d90691")

    # async def search_github(self, username: str):
    #     """Парсинг GitHub"""
    #     url = f"https://api.github.com/users/{username}"
    #     headers = {}
    #     if self.github_token:
    #         headers["Authorization"] = f"token {self.github_token}"

    #     try:
    #         async with aiohttp.ClientSession() as session:
    #             async with session.get(url, headers=headers, timeout=10) as response:
    #                 if response.status == 200:
    #                     data = await response.json()
    #                     return {
    #                         "source": "GitHub",
    #                         "name": data.get("name"),
    #                         "handle": f"github.com/{data.get('login')}",
    #                         "avatar": data.get("avatar_url"),
    #                         "bio": data.get("bio")
    #                     }
    #                 elif response.status == 404:
    #                     return None
    #     except:
    #         pass
    #     return None

    async def search_vk(self, query: str):
        """Упрощенный поиск по VK (поиск по ID или скриннейму)"""
        url = f"https://www.vk.com/{query}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200 and "Поиск по ID" not in response.text() and "Ошибка" not in response.text():
                        # Для простоты считаем, что это он, если страница открылась нормально
                        # В реальном проекте нужно парсить HTML для имени и фото
                        return {
                            "source": "VKontakte",
                            "handle": f"vk.com/{query}",
                            "name": "Пользователь",
                            "avatar": "https://sun9-67.userapi.com/..."
                        }
        except:
            pass
        return None

    async def search_phone(self, phone: str):
        """Поиск по номеру телефона (через пример API)"""
        if not self.phone_api_token:
            return None

        # Пример API (можно заменить на свой, например smotrim.io или truecaller.com)
        # Упрощенный пример: возвращаем заглушку, если API платный
        return {
            "source": "Phone DB (Example)",
            "name": f"Человек с номером {phone}",
            "handle": phone,
            "avatar": "https://example.com/avatar.png"
        }

async def aggregate_search(query: str, is_phone: bool = False):
    """Запускает поиск по всем источникам параллельно"""
    engine = SearchEngine()
    tasks = []

    if not is_phone:
        tasks.append(engine.search_github(query))
        tasks.append(engine.search_vk(query))
    else:
        tasks.append(engine.search_phone(query))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    found_results = [r for r in results if r is not None]
    return found_results