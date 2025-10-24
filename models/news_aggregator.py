"""
Модель для сбора и обработки новостей
"""

import json
import logging
import os
import time
from typing import Dict, List, Optional
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

from config.settings import Settings

logger = logging.getLogger(__name__)


class NewsAggregator:
    """Класс для сбора и обработки новостей из RSS-каналов"""

    def __init__(self):
        self.sources = Settings.SOURCES
        self.filter_keywords = Settings.FILTER_KEYWORDS
        self.database_path = Settings.DATABASE_PATH
        self.max_news_count = Settings.MAX_NEWS_COUNT

    def load_news_data(self) -> List[Dict]:
        """Загружает новости из файла"""
        try:
            if os.path.exists(self.database_path):
                with open(self.database_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки новостей: {e}")
        return []

    def save_news_data(self, data: List[Dict]) -> None:
        """Сохраняет новости в файл"""
        try:
            os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
            with open(self.database_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения новостей: {e}")

    def fetch_news_from_rss(self, url: str) -> List[Dict]:
        """Получает новости из RSS-канала"""
        news_list = []
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                logger.warning(f"Проблемы с парсингом RSS: {url}")
                return news_list

            for entry in feed.entries:
                try:
                    # Извлекаем текст из описания
                    description = self._extract_description(entry)

                    # Определяем тему на основе заголовка и описания
                    topic = self._detect_topic(entry.title, description)

                    # Проверяем фильтры
                    if self._should_filter(entry.title, description):
                        continue

                    news_item = {
                        'id': f"{urlparse(url).netloc}_{hash(entry.link)}",
                        'title': entry.title,
                        'link': entry.link,
                        'description': description[:500] + "..." if len(description) > 500 else description,
                        'source': urlparse(url).netloc,
                        'topic': topic,
                        'published': entry.get('published_parsed', time.gmtime()),
                        'timestamp': time.time()
                    }
                    news_list.append(news_item)

                except Exception as e:
                    logger.error(f"Ошибка обработки новости: {e}")
                    continue

        except Exception as e:
            logger.error(f"Ошибка получения RSS: {url}, {e}")

        return news_list

    def _extract_description(self, entry) -> str:
        """Извлекает описание из записи RSS"""
        description = ""

        if hasattr(entry, 'summary'):
            soup = BeautifulSoup(entry.summary, 'html.parser')
            description = soup.get_text().strip()
        elif hasattr(entry, 'description'):
            soup = BeautifulSoup(entry.description, 'html.parser')
            description = soup.get_text().strip()

        return description

    def _detect_topic(self, title: str, description: str) -> str:
        """Определяет тему новости на основе заголовка и описания"""
        text = f"{title} {description}".lower()

        topics = {
            'экономика': [
                'экономика', 'экономический', 'экономист', 'экономические', 'экономике',
                'economy', 'economic', 'economics', 'economist', 'macroeconomics', 'microeconomics', 'growth', 'gdp', 'inflation', 'recession'
            ],

            'финансы': [
                'финансы', 'финансовый', 'финансовые', 'банк', 'банки', 'кредит', 'деньги',
                'finance', 'financial', 'bank', 'banks', 'credit', 'money', 'loan', 'monetary', 'cash', 'budget', 'liquidity', 'debt', 'funding'
            ],

            'рынки': [
                'рынок', 'рынки', 'торговля', 'торговый', 'акции', 'облигации', 'индекс',
                'market', 'markets', 'trade', 'trading', 'stocks', 'shares', 'bonds', 'index', 'indices', 'commodities', 'forex', 'exchange', 'derivatives'
            ],

            'технологии': [
                'технология', 'технологии', 'технологический', 'инновации', 'стартап',
                'technology', 'technologies', 'tech', 'innovation', 'innovations', 'startup', 'startups', 'ai', 'artificial intelligence', 'machine learning', 'blockchain', 'fintech', 'digital', 'automation', 'software'
            ],

            'инвестиции': [
                'инвестиции', 'инвестиционный', 'инвестор', 'капитал', 'портфель',
                'investment', 'investments', 'investor', 'investors', 'capital', 'portfolio', 'venture', 'fund', 'funds', 'asset', 'equity', 'returns', 'valuation', 'securities'
            ]
        }

        for topic, keywords in topics.items():
            if any(keyword in text for keyword in keywords):
                return topic

        return 'общее'

    def _should_filter(self, title: str, description: str) -> bool:
        """Проверяет, нужно ли фильтровать новость"""
        if not self.filter_keywords:
            return False

        text = f"{title} {description}".lower()
        return any(keyword in text for keyword in self.filter_keywords)

    def collect_news(self) -> List[Dict]:
        """Собирает новости из всех источников"""
        all_news = []

        for source in self.sources:
            logger.info(f"Сбор новостей из: {source}")
            news = self.fetch_news_from_rss(source)
            all_news.extend(news)
            logger.info(f"Получено {len(news)} новостей из {source}")

        # Удаляем дубликаты
        seen_ids = set()
        unique_news = []
        for news in all_news:
            if news['id'] not in seen_ids:
                seen_ids.add(news['id'])
                unique_news.append(news)

        return unique_news

    def update_news_database(self) -> None:
        """Обновляет базу данных новостей"""
        # Загружаем существующие новости
        news_data = self.load_news_data()

        # Собираем новые новости
        new_news = self.collect_news()

        # Добавляем новые новости
        existing_ids = {news['id'] for news in news_data}
        for news in new_news:
            if news['id'] not in existing_ids:
                news_data.append(news)

        # Сортируем по времени публикации (новые сначала)
        news_data.sort(key=lambda x: x['timestamp'], reverse=True)

        # Ограничиваем количество новостей
        if len(news_data) > self.max_news_count:
            news_data = news_data[:self.max_news_count]

        # Сохраняем обновленные данные
        self.save_news_data(news_data)
        logger.info(f"База данных обновлена. Всего новостей: {len(news_data)}")

    def get_news_by_topics(self, topics: List[str], limit: int = None, page: int = 1) -> List[Dict]:
        """Получает новости по заданным темам"""
        news_data = self.load_news_data()
        filtered_news = [news for news in news_data if news['topic'] in topics]

        if limit and page:
            return filtered_news[(page-1)*limit:(page)*limit]
        return filtered_news

    def search_news(self, query: str, topics: List[str] = None) -> List[Dict]:
        """Ищет новости по запросу"""
        news_data = self.load_news_data()

        # Ищем по запросу
        query_lower = query.lower()
        results = []

        for news in news_data:
            if (query_lower in news['topic'].lower()):
                results.append(news)

        return news_data

    def get_news_by_id(self, news_id: str) -> Optional[Dict]:
        """Получает новость по ID"""
        news_data = self.load_news_data()
        for news in news_data:
            if news['id'] == news_id:
                return news
        return None
