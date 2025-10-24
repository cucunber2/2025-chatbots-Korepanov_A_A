"""
Планировщик задач
"""

import asyncio
import logging
import schedule
import time
from typing import Callable

from config.settings import Settings

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Класс для планирования периодических задач"""
    
    def __init__(self):
        self.is_running = False
        self.tasks = []
    
    def add_daily_task(self, time_str: str, task_func: Callable, *args, **kwargs):
        """Добавляет ежедневную задачу"""
        schedule.every().day.at(time_str).do(
            lambda: asyncio.create_task(task_func(*args, **kwargs))
        )
        logger.info(f"Добавлена ежедневная задача на {time_str}")
    
    def add_interval_task(self, interval_seconds: int, task_func: Callable, *args, **kwargs):
        """Добавляет задачу с интервалом"""
        schedule.every(interval_seconds).seconds.do(
            lambda: asyncio.create_task(task_func(*args, **kwargs))
        )
        logger.info(f"Добавлена задача с интервалом {interval_seconds} секунд")
    
    async def start(self):
        """Запускает планировщик"""
        self.is_running = True
        logger.info("Планировщик запущен")
        
        while self.is_running:
            try:
                schedule.run_pending()
                await asyncio.sleep(Settings.SCHEDULER_CHECK_INTERVAL)
            except Exception as e:
                logger.error(f"Ошибка в планировщике: {e}")
                await asyncio.sleep(60)  # Ждем минуту при ошибке
    
    def stop(self):
        """Останавливает планировщик"""
        self.is_running = False
        logger.info("Планировщик остановлен")
    
    def clear_tasks(self):
        """Очищает все задачи"""
        schedule.clear()
        logger.info("Все задачи очищены")


# Глобальный экземпляр планировщика
scheduler = TaskScheduler()
