"""
Контроллер для обработки команд бота
"""

import logging
from typing import List, Dict, Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from models import NewsAggregator, UserManager
from views import MessageFormatter
from config.settings import Settings

logger = logging.getLogger(__name__)


class BotController:
    """Основной контроллер бота"""

    def __init__(self, bot: Bot, dp: Dispatcher):
        self.bot = bot
        self.dp = dp
        self.news_aggregator = NewsAggregator()
        self.user_manager = UserManager()
        self.formatter = MessageFormatter()
        self._register_handlers()

    def _register_handlers(self):
        """Регистрирует обработчики команд"""
        self.dp.message.register(self.start_command, CommandStart())
        self.dp.message.register(self.help_command, Command("help"))
        self.dp.message.register(self.add_topic_command, Command("addtopic"))
        self.dp.message.register(
            self.remove_topic_command, Command("removetopic"))
        self.dp.message.register(self.my_topics_command, Command("mytopics"))
        self.dp.message.register(self.latest_command, Command("latest"))
        self.dp.message.register(self.search_command, Command("search"))
        self.dp.message.register(self.favorites_command, Command("favorites"))
        self.dp.message.register(self.save_command, Command("save"))

    async def start_command(self, message: Message):
        """Обработчик команды /start"""
        user_id = str(message.from_user.id)
        self.user_manager.update_user_activity(user_id)

        welcome_text = self.formatter.format_welcome_message()
        await message.answer(welcome_text)

    async def help_command(self, message: Message):
        """Обработчик команды /help"""
        user_id = str(message.from_user.id)
        self.user_manager.update_user_activity(user_id)

        help_text = self.formatter.format_help_message()
        await message.answer(help_text)

    async def add_topic_command(self, message: Message):
        """Обработчик команды /addtopic"""
        user_id = str(message.from_user.id)
        self.user_manager.update_user_activity(user_id)

        try:
            topic = message.text.split(' ', 1)[1].strip().lower()

            if not self.user_manager.is_topic_valid(topic):
                await message.answer(
                    self.formatter.format_error_message('invalid_topic')
                )
                return

            if self.user_manager.add_topic(user_id, topic):
                await message.answer(
                    self.formatter.format_success_message(
                        'topic_added', f"Тема '{topic}' добавлена!")
                )
            else:
                await message.answer(
                    self.formatter.format_error_message(
                        'topic_already_exists', f"Тема '{topic}' уже была добавлена ранее")
                )

        except IndexError:
            await message.answer(
                self.formatter.format_error_message('missing_topic')
            )

    async def remove_topic_command(self, message: Message):
        """Обработчик команды /removetopic"""
        user_id = str(message.from_user.id)
        self.user_manager.update_user_activity(user_id)

        try:
            topic = message.text.split(' ', 1)[1].strip().lower()

            if self.user_manager.remove_topic(user_id, topic):
                await message.answer(
                    self.formatter.format_success_message(
                        'topic_removed', f"Тема '{topic}' удалена!")
                )
            else:
                await message.answer(
                    self.formatter.format_error_message(
                        'topic_not_found', f"Тема '{topic}' не была найдена в вашем списке")
                )

        except IndexError:
            await message.answer(
                self.formatter.format_error_message('missing_topic')
            )

    async def my_topics_command(self, message: Message):
        """Обработчик команды /mytopics"""
        user_id = str(message.from_user.id)
        self.user_manager.update_user_activity(user_id)

        topics = self.user_manager.get_user_topics(user_id)
        topics_text = self.formatter.format_topics_list(topics)
        await message.answer(topics_text)

    async def latest_command(self, message: Message):
        """Обработчик команды /latest"""
        user_id = str(message.from_user.id)
        self.user_manager.update_user_activity(user_id)

        text_parts = message.text.split(' ', 1)
        page = 1

        if len(text_parts) > 1:
            arg = text_parts[1].strip()
            if arg.isdigit():
                page = int(arg)

        topics = self.user_manager.get_user_topics(user_id)
        if not topics:
            await message.answer(
                self.formatter.format_error_message('no_topics')
            )
            return

        # Получаем последние новости по темам пользователя
        user_news = self.news_aggregator.get_news_by_topics(
            topics, Settings.DIGEST_SIZE, page)

        if not user_news:
            await message.answer("❌ Новостей по вашим темам не найдено")
            return

        response = self.formatter.format_news_list(
            user_news, "📰 Последние новости", Settings.DIGEST_SIZE, page)
        await message.answer(response)

    async def search_command(self, message: Message):
        """Обработчик команды /search"""
        user_id = str(message.from_user.id)
        self.user_manager.update_user_activity(user_id)

        try:
            query = message.text.split(' ', 1)[1].strip()
            topics = self.user_manager.get_user_topics(user_id)

            # Ищем новости по запросу и темам пользователя
            search_results = self.news_aggregator.search_news(query, topics)

            if not search_results:
                await message.answer(
                    self.formatter.format_error_message(
                        'no_results', f"По запросу '{query}' ничего не найдено")
                )
                return

            # Берем первые результаты
            results = search_results[:Settings.DIGEST_SIZE]
            response = self.formatter.format_search_results(query, results)
            await message.answer(response)

        except IndexError:
            await message.answer(
                self.formatter.format_error_message('missing_query')
            )

    async def favorites_command(self, message: Message):
        """Обработчик команды /favorites"""
        user_id = str(message.from_user.id)
        self.user_manager.update_user_activity(user_id)

        favorite_ids = self.user_manager.get_user_favorites(user_id)

        if not favorite_ids:
            await message.answer("⭐ У вас пока нет сохранённых новостей")
            return

        # Получаем новости по ID
        favorites = []
        for news_id in favorite_ids:
            news = self.news_aggregator.get_news_by_id(news_id)
            if news:
                favorites.append(news)

        if not favorites:
            await message.answer("⭐ Сохранённые новости больше не доступны")
            return

        response = self.formatter.format_favorites(favorites)
        await message.answer(response)

    async def save_command(self, message: Message):
        """Обработчик команды /save"""
        user_id = str(message.from_user.id)
        self.user_manager.update_user_activity(user_id)

        try:
            news_number = int(message.text.split(' ', 1)[1].strip())
            topics = self.user_manager.get_user_topics(user_id)

            # Получаем новости по темам пользователя
            user_news = self.news_aggregator.get_news_by_topics(
                topics)

            if 1 <= news_number <= len(user_news):
                news = user_news[news_number - 1]
                if self.user_manager.add_favorite(user_id, news['id']):
                    await message.answer(
                        self.formatter.format_success_message(
                            'news_saved', f"Новость '{news['title'][:50]}...' сохранена в избранное!")
                    )
                else:
                    await message.answer("⚠️ Эта новость уже была сохранена ранее")
            else:
                await message.answer(
                    self.formatter.format_error_message(
                        'invalid_news_number', self.formatter.format_news_range(len(user_news)))
                )

        except (IndexError, ValueError):
            await message.answer(
                self.formatter.format_error_message('missing_news_number')
            )

    async def send_daily_digest_to_user(self, user_id: str, user_topics: List[str]) -> bool:
        """Отправляет ежедневный дайджест пользователю"""
        try:
            # Получаем новости по темам пользователя
            user_news = self.news_aggregator.get_news_by_topics(
                user_topics, Settings.DIGEST_SIZE)

            if not user_news:
                return False

            digest_text = self.formatter.format_daily_digest(user_news)
            await self.bot.send_message(user_id, digest_text)
            logger.info(f"Дайджест отправлен пользователю {user_id}")
            return True

        except Exception as e:
            logger.error(
                f"Ошибка отправки дайджеста пользователю {user_id}: {e}")
            return False

    async def send_daily_digest_to_all_users(self):
        """Отправляет ежедневный дайджест всем пользователям"""
        users_with_topics = self.user_manager.get_users_with_topics()

        if not users_with_topics:
            logger.info("Нет пользователей для отправки дайджеста")
            return

        for user_id, user_info in users_with_topics.items():
            topics = user_info.get('topics', [])
            if topics:
                await self.send_daily_digest_to_user(user_id, topics)

    def get_news_aggregator(self) -> NewsAggregator:
        """Возвращает экземпляр NewsAggregator"""
        return self.news_aggregator

    def get_user_manager(self) -> UserManager:
        """Возвращает экземпляр UserManager"""
        return self.user_manager
