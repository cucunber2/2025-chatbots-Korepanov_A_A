"""
Конфигурационные настройки бота
"""

import os, json
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


class Settings:
    """Класс для хранения всех настроек приложения"""
    
    # Telegram Bot
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    
    # Пути к файлам данных
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/news.json')
    USERS_PATH = os.getenv('USERS_PATH', 'data/users.json')
    
    # RSS источники
    SOURCES = []

    with open(os.getenv("SOURCES_FILE", "sources.json")) as f:
        SOURCES = [source.strip() for source in json.load(f) if source.strip()]
    
    # Настройки времени
    TIMEZONE = os.getenv('TIMEZONE', 'Europe/Moscow')
    DAILY_TIME = os.getenv('DAILY_TIME', '09:00')
    
    # Настройки дайджеста
    DIGEST_SIZE = int(os.getenv('DIGEST_SIZE', '10'))
    MAX_NEWS_COUNT = int(os.getenv('MAX_NEWS_COUNT', '1000'))
    
    # Фильтрация
    FILTER_KEYWORDS = [kw.strip().lower() for kw in os.getenv('FILTER_KEYWORDS', '').split(',') if kw.strip()]
    
    # Доступные темы
    AVAILABLE_TOPICS = ['экономика', 'финансы', 'рынки', 'технологии', 'инвестиции', 'общее']
    
    # Настройки логирования
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs.txt')
    
    # Интервалы обновления
    NEWS_UPDATE_INTERVAL = int(os.getenv('NEWS_UPDATE_INTERVAL', '1800'))  # 30 минут в секундах
    SCHEDULER_CHECK_INTERVAL = int(os.getenv('SCHEDULER_CHECK_INTERVAL', '60'))  # 1 минута
    
    @classmethod
    def validate(cls) -> bool:
        """Проверяет корректность настроек"""
        if not cls.TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_TOKEN не установлен")
        
        if not cls.SOURCES:
            raise ValueError("Не указаны RSS источники")
        
        return True
