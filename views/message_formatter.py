"""
Форматирование сообщений для пользователей
"""

from typing import List, Dict, Optional
from config.settings import Settings


class MessageFormatter:
    """Класс для форматирования сообщений бота"""
    
    @staticmethod
    def format_welcome_message() -> str:
        """Форматирует приветственное сообщение"""
        return """
📰 Добро пожаловать в бот-агрегатор финансовых новостей!

Я помогу вам:
• Получать свежие новости по интересующим темам
• Создавать ежедневные дайджесты
• Искать новости по ключевым словам
• Сохранять понравившиеся статьи

Доступные команды:
/help - показать все команды
/addtopic [тема] - добавить тему
/removetopic [тема] - удалить тему
/mytopics - мои темы
/latest - последние новости
/search [запрос] - поиск новостей
/favorites - избранное
/save [номер] - сохранить в избранное

Начните с добавления интересующих тем!
"""
    
    @staticmethod
    def format_help_message() -> str:
        """Форматирует справочное сообщение"""
        return """
📋 Доступные команды:

/start - приветствие и описание
/help - показать эту справку

📚 Управление темами:
/addtopic [тема] - добавить новую тему
/removetopic [тема] - удалить тему
/mytopics - показать мои темы

📰 Просмотр новостей:
/latest - последние 5 новостей
/search [запрос] - найти новости по ключевым словам

⭐ Избранное:
/favorites - показать сохранённые материалы
/save [номер] - сохранить новость в избранное

Доступные темы: экономика, финансы, рынки, технологии, инвестиции
"""
    
    @staticmethod
    def format_topics_list(topics: List[str]) -> str:
        """Форматирует список тем пользователя"""
        if topics:
            topics_text = "📚 Ваши темы:\n" + "\n".join(f"• {topic}" for topic in topics)
        else:
            topics_text = "📚 У вас пока нет выбранных тем. Используйте /addtopic для добавления"
        
        return topics_text
    
    @staticmethod
    def format_news_list(news_list: List[Dict], title: str = "📰 Новости", limit: int = 10, page: int = 1) -> str:
        """Форматирует список новостей"""
        if not news_list:
            return "❌ Новости не найдены"
        
        response = f"{title} (Страница {page}):\n\n"
        for i, news in enumerate(news_list, 1):
            response += f"{i + (page-1) * limit}. {news['title']}\n"
            response += f"   📅 {news['source']} | {news['topic']}\n"
            response += f"   📝 {news['description'][:100]}...\n"
            response += f"   🔗 {news['link']}\n\n"
        
        return response
    
    @staticmethod
    def format_search_results(query: str, results: List[Dict]) -> str:
        """Форматирует результаты поиска"""
        if not results:
            return f"❌ По запросу '{query}' ничего не найдено"
        
        response = f"🔍 Результаты поиска по запросу '{query}':\n\n"
        for i, news in enumerate(results, 1):
            response += f"{i}. {news['title']}\n"
            response += f"   📅 {news['source']} | {news['topic']}\n"
            response += f"   📝 {news['description'][:100]}...\n"
            response += f"   🔗 {news['link']}\n\n"
        
        return response
    
    @staticmethod
    def format_favorites(favorites: List[Dict]) -> str:
        """Форматирует список избранного"""
        if not favorites:
            return "⭐ У вас пока нет сохранённых новостей"
        
        response = "⭐ Ваши сохранённые новости:\n\n"
        for i, news in enumerate(favorites, 1):
            response += f"{i}. {news['title']}\n"
            response += f"   📅 {news['source']} | {news['topic']}\n"
            response += f"   📝 {news['description'][:100]}...\n"
            response += f"   🔗 {news['link']}\n\n"
        
        return response
    
    @staticmethod
    def format_daily_digest(news_list: List[Dict]) -> str:
        """Форматирует ежедневный дайджест"""
        if not news_list:
            return "📰 На сегодня новостей нет"
        
        digest_text = f"📰 Ежедневный дайджест новостей\n\n"
        for i, news in enumerate(news_list, 1):
            digest_text += f"{i}. {news['title']}\n"
            digest_text += f"   📅 {news['source']} | {news['topic']}\n"
            digest_text += f"   📝 {news['description'][:100]}...\n"
            digest_text += f"   🔗 {news['link']}\n\n"
        
        return digest_text
    
    @staticmethod
    def format_error_message(error_type: str, details: str = "") -> str:
        """Форматирует сообщение об ошибке"""
        error_messages = {
            'no_topics': "❌ Сначала добавьте интересующие темы командой /addtopic",
            'invalid_topic': f"❌ Неизвестная тема. Доступные темы: {', '.join(Settings.AVAILABLE_TOPICS)}",
            'topic_already_exists': "⚠️ Эта тема уже была добавлена ранее",
            'topic_not_found': "⚠️ Эта тема не была найдена в вашем списке",
            'invalid_news_number': "❌ Неверный номер новости",
            'news_already_saved': "⚠️ Эта новость уже была сохранена ранее",
            'missing_query': "❌ Укажите поисковый запрос. Пример: /search экономика",
            'missing_topic': "❌ Укажите тему. Пример: /addtopic экономика",
            'missing_news_number': "❌ Укажите номер новости. Пример: /save 1"
        }
        
        base_message = error_messages.get(error_type, "❌ Произошла ошибка")
        if details:
            return f"{base_message}\n{details}"
        return base_message
    
    @staticmethod
    def format_success_message(message_type: str, details: str = "") -> str:
        """Форматирует сообщение об успехе"""
        success_messages = {
            'topic_added': "✅ Тема добавлена!",
            'topic_removed': "✅ Тема удалена!",
            'news_saved': "✅ Новость сохранена в избранное!",
            'news_removed': "✅ Новость удалена из избранного!"
        }
        
        base_message = success_messages.get(message_type, "✅ Операция выполнена успешно")
        if details:
            return f"{base_message}\n{details}"
        return base_message
    
    @staticmethod
    def format_available_topics() -> str:
        """Форматирует список доступных тем"""
        return f"📋 Доступные темы: {', '.join(Settings.AVAILABLE_TOPICS)}"
    
    @staticmethod
    def format_news_range(max_number: int) -> str:
        """Форматирует диапазон доступных номеров новостей"""
        return f"Доступно: 1-{max_number}"
