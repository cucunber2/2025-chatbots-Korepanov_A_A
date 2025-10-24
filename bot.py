#!/usr/bin/env python3
"""
Telegram-бот-агрегатор финансовых новостей
Собирает новости из RSS-каналов и отправляет ежедневные дайджесты пользователям

Архитектура: MVC (Model-View-Controller)
"""

import asyncio
import sys
from typing import Optional

from aiogram import Bot, Dispatcher

from config.settings import Settings
from controllers import BotController
from models import NewsAggregator, UserManager
from utils import setup_logging, get_logger, scheduler

# Настройка логирования
setup_logging()
logger = get_logger(__name__)


class NewsBot:
    """Основной класс бота"""
    
    def __init__(self):
        self.bot: Optional[Bot] = None
        self.dp: Optional[Dispatcher] = None
        self.controller: Optional[BotController] = None
        self.news_aggregator: Optional[NewsAggregator] = None
        self.user_manager: Optional[UserManager] = None
        
    def initialize(self):
        """Инициализирует компоненты бота"""
        try:
            # Валидация настроек
            Settings.validate()
            
            # Инициализация бота и диспетчера
            self.bot = Bot(token=Settings.TELEGRAM_TOKEN)
            self.dp = Dispatcher()
            
            # Инициализация моделей
            self.news_aggregator = NewsAggregator()
            self.user_manager = UserManager()
            
            # Инициализация контроллера
            self.controller = BotController(self.bot, self.dp)
            
            # Настройка планировщика задач
            self._setup_scheduler()
            
            logger.info("Бот успешно инициализирован")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации бота: {e}")
            raise
    
    def _setup_scheduler(self):
        """Настраивает планировщик задач"""
        # Ежедневный дайджест
        scheduler.add_daily_task(
            Settings.DAILY_TIME,
            self.controller.send_daily_digest_to_all_users
        )
        
        # Периодическое обновление новостей
        scheduler.add_interval_task(
            Settings.NEWS_UPDATE_INTERVAL,
            self._update_news_task
        )
        
        # Очистка неактивных пользователей (раз в неделю)
        scheduler.add_interval_task(
            7 * 24 * 60 * 60,  # 7 дней
            self._cleanup_users_task
        )
        
        logger.info("Планировщик задач настроен")
    
    async def _update_news_task(self):
        """Задача обновления новостей"""
        try:
            logger.info("Запуск обновления новостей...")
            self.news_aggregator.update_news_database()
            logger.info("Новости успешно обновлены")
        except Exception as e:
            logger.error(f"Ошибка обновления новостей: {e}")
    
    async def _cleanup_users_task(self):
        """Задача очистки неактивных пользователей"""
        try:
            logger.info("Запуск очистки неактивных пользователей...")
            cleaned_count = self.user_manager.cleanup_inactive_users()
            logger.info(f"Очищено {cleaned_count} неактивных пользователей")
        except Exception as e:
            logger.error(f"Ошибка очистки пользователей: {e}")
    
    async def start(self):
        """Запускает бота"""
        try:
            logger.info("Запуск бота...")
            
            # Первоначальное обновление новостей
            await self._update_news_task()
            
            # Запуск планировщика в фоне
            asyncio.create_task(scheduler.start())
            
            # Запуск бота
            await self.dp.start_polling(self.bot)
            
        except Exception as e:
            logger.error(f"Ошибка запуска бота: {e}")
            raise
    
    async def stop(self):
        """Останавливает бота"""
        try:
            logger.info("Остановка бота...")
            scheduler.stop()
            await self.bot.session.close()
            logger.info("Бот остановлен")
        except Exception as e:
            logger.error(f"Ошибка остановки бота: {e}")
    
    def get_status(self) -> dict:
        """Возвращает статус бота"""
        return {
            'initialized': self.controller is not None,
            'news_count': len(self.news_aggregator.load_news_data()) if self.news_aggregator else 0,
            'users_count': len(self.user_manager.get_all_users()) if self.user_manager else 0,
            'scheduler_running': scheduler.is_running
        }


async def main():
    """Основная функция"""
    bot_instance = NewsBot()
    
    try:
        # Инициализация
        bot_instance.initialize()
        
        # Вывод статуса
        status = bot_instance.get_status()
        logger.info(f"Статус бота: {status}")
        
        # Запуск
        await bot_instance.start()
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        await bot_instance.stop()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)