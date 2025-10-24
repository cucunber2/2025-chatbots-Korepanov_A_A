"""
Модель для управления пользователями
"""

import json
import logging
import os
import time
from typing import Dict, List, Optional

from config.settings import Settings

logger = logging.getLogger(__name__)


class UserManager:
    """Класс для управления пользователями и их настройками"""
    
    def __init__(self):
        self.users_path = Settings.USERS_PATH
        self.users_data = {}
        self.load_users_data()
    
    def load_users_data(self) -> None:
        """Загружает данные пользователей из файла"""
        try:
            if os.path.exists(self.users_path):
                with open(self.users_path, 'r', encoding='utf-8') as f:
                    self.users_data = json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки пользователей: {e}")
            self.users_data = {}
    
    def save_users_data(self) -> None:
        """Сохраняет данные пользователей в файл"""
        try:
            os.makedirs(os.path.dirname(self.users_path), exist_ok=True)
            with open(self.users_path, 'w', encoding='utf-8') as f:
                json.dump(self.users_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения пользователей: {e}")
    
    def get_user(self, user_id: str) -> Dict:
        """Получает данные пользователя"""
        if user_id not in self.users_data:
            self.users_data[user_id] = {
                'topics': [],
                'favorites': [],
                'created_at': time.time(),
                'last_activity': time.time()
            }
        return self.users_data[user_id]
    
    def update_user_activity(self, user_id: str) -> None:
        """Обновляет время последней активности пользователя"""
        user = self.get_user(user_id)
        user['last_activity'] = time.time()
        self.save_users_data()
    
    def add_topic(self, user_id: str, topic: str) -> bool:
        """Добавляет тему для пользователя"""
        if topic not in Settings.AVAILABLE_TOPICS:
            return False
            
        user = self.get_user(user_id)
        if topic not in user['topics']:
            user['topics'].append(topic)
            self.save_users_data()
            return True
        return False
    
    def remove_topic(self, user_id: str, topic: str) -> bool:
        """Удаляет тему для пользователя"""
        user = self.get_user(user_id)
        if topic in user['topics']:
            user['topics'].remove(topic)
            self.save_users_data()
            return True
        return False
    
    def get_user_topics(self, user_id: str) -> List[str]:
        """Получает список тем пользователя"""
        user = self.get_user(user_id)
        return user['topics']
    
    def add_favorite(self, user_id: str, news_id: str) -> bool:
        """Добавляет новость в избранное"""
        user = self.get_user(user_id)
        if news_id not in user['favorites']:
            user['favorites'].append(news_id)
            self.save_users_data()
            return True
        return False
    
    def remove_favorite(self, user_id: str, news_id: str) -> bool:
        """Удаляет новость из избранного"""
        user = self.get_user(user_id)
        if news_id in user['favorites']:
            user['favorites'].remove(news_id)
            self.save_users_data()
            return True
        return False
    
    def get_user_favorites(self, user_id: str) -> List[str]:
        """Получает список избранных новостей пользователя"""
        user = self.get_user(user_id)
        return user['favorites']
    
    def get_all_users(self) -> Dict[str, Dict]:
        """Получает всех пользователей"""
        return self.users_data
    
    def get_users_with_topics(self) -> Dict[str, Dict]:
        """Получает пользователей с выбранными темами"""
        return {
            user_id: user_data 
            for user_id, user_data in self.users_data.items() 
            if user_data.get('topics')
        }
    
    def is_topic_valid(self, topic: str) -> bool:
        """Проверяет, является ли тема валидной"""
        return topic in Settings.AVAILABLE_TOPICS
    
    def get_available_topics(self) -> List[str]:
        """Получает список доступных тем"""
        return Settings.AVAILABLE_TOPICS.copy()
    
    def cleanup_inactive_users(self, days_inactive: int = 30) -> int:
        """Удаляет неактивных пользователей"""
        current_time = time.time()
        inactive_threshold = current_time - (days_inactive * 24 * 60 * 60)
        
        inactive_users = []
        for user_id, user_data in self.users_data.items():
            last_activity = user_data.get('last_activity', 0)
            if last_activity < inactive_threshold:
                inactive_users.append(user_id)
        
        for user_id in inactive_users:
            del self.users_data[user_id]
        
        if inactive_users:
            self.save_users_data()
            logger.info(f"Удалено {len(inactive_users)} неактивных пользователей")
        
        return len(inactive_users)
