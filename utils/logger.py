"""
Настройка логирования
"""

import logging
import os
from config.settings import Settings


def setup_logging():
    """Настраивает логирование для приложения"""
    # Создаем директорию для логов если её нет
    log_dir = os.path.dirname(Settings.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Настраиваем уровень логирования
    log_level = getattr(logging, Settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Очищаем существующие обработчики
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Создаем обработчик для файла
    file_handler = logging.FileHandler(Settings.LOG_FILE, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Создаем обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчики
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Настраиваем логгеры для внешних библиотек
    logging.getLogger('aiogram').setLevel(logging.WARNING)
    logging.getLogger('feedparser').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Получает логгер с заданным именем"""
    return logging.getLogger(name)
