# Makefile для Telegram-бота-агрегатора финансовых новостей

.PHONY: help install setup run test clean deactivate activate status

# Переменные
PYTHON = python
PIP = pip
VENV_DIR = venv
VENV_ACTIVATE = $(VENV_DIR)/bin/activate
VENV_PYTHON = $(VENV_DIR)/bin/python
VENV_PIP = $(VENV_DIR)/bin/pip

# Цвета для вывода
BLUE = \033[0;34m
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

# Помощь
help: ## Показать справку по командам
	@echo "$(BLUE)Доступные команды:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Примеры использования:$(NC)"
	@echo "  make setup     # Полная настройка проекта"
	@echo "  make install   # Установка зависимостей"
	@echo "  make run       # Запуск бота"
	@echo "  make test      # Тестирование"

# Полная настройка проекта
setup: ## Полная настройка проекта (создание venv, установка зависимостей, настройка конфигурации)
	@echo "$(BLUE)🚀 Настройка проекта...$(NC)"
	@chmod +x setup.sh
	@./setup.sh
	@echo "$(GREEN)✅ Настройка завершена!$(NC)"

# Создание виртуального окружения
venv: ## Создать виртуальное окружение
	@echo "$(BLUE)Создание виртуального окружения...$(NC)"
	@$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(GREEN)✅ Виртуальное окружение создано$(NC)"

# Активация виртуального окружения
activate: ## Активировать виртуальное окружение
	@echo "$(BLUE)Активация виртуального окружения...$(NC)"
	@echo "Выполните: source $(VENV_ACTIVATE)"
	@echo "$(YELLOW)Или используйте: make run$(NC)"

# Деактивация виртуального окружения
deactivate: ## Деактивировать виртуальное окружение
	@echo "$(BLUE)Деактивация виртуального окружения...$(NC)"
	@echo "Выполните: deactivate"

# Установка зависимостей
install: venv ## Установить зависимости
	@echo "$(BLUE)Установка зависимостей...$(NC)"
	@$(VENV_PIP) install --upgrade pip
	@$(VENV_PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Зависимости установлены$(NC)"

# Обновление зависимостей
update: ## Обновить зависимости
	@echo "$(BLUE)Обновление зависимостей...$(NC)"
	@$(VENV_PIP) install --upgrade -r requirements.txt
	@echo "$(GREEN)✅ Зависимости обновлены$(NC)"

# Создание конфигурации
config: ## Создать файл конфигурации
	@echo "$(BLUE)Создание конфигурации...$(NC)"
	@if [ ! -f .env ]; then \
		cp env_example.txt .env; \
		echo "$(GREEN)✅ Файл .env создан из примера$(NC)"; \
		echo "$(YELLOW)⚠️  Не забудьте отредактировать .env и добавить токен бота$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Файл .env уже существует$(NC)"; \
	fi
	@mkdir -p data
	@echo "$(GREEN)✅ Директории созданы$(NC)"

# Запуск бота
run: ## Запустить бота
	@echo "$(BLUE)Запуск бота...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(RED)❌ Файл .env не найден. Выполните: make config$(NC)"; \
		exit 1; \
	fi
	@if [ ! -d $(VENV_DIR) ]; then \
		echo "$(RED)❌ Виртуальное окружение не найдено. Выполните: make install$(NC)"; \
		exit 1; \
	fi
	@$(VENV_PYTHON) bot.py

# Тестирование
test: ## Запустить тесты
	@echo "$(BLUE)Запуск тестов...$(NC)"
	@if [ ! -d $(VENV_DIR) ]; then \
		echo "$(RED)❌ Виртуальное окружение не найдено. Выполните: make install$(NC)"; \
		exit 1; \
	fi
	@$(VENV_PYTHON) -c "import aiogram, feedparser, requests, schedule; print('✅ Все зависимости работают')"

# Проверка статуса
status: ## Показать статус проекта
	@echo "$(BLUE)Статус проекта:$(NC)"
	@echo ""
	@echo "📁 Структура файлов:"
	@if [ -f bot.py ]; then echo "  ✅ bot.py"; else echo "  ❌ bot.py"; fi
	@if [ -f requirements.txt ]; then echo "  ✅ requirements.txt"; else echo "  ❌ requirements.txt"; fi
	@if [ -f .env ]; then echo "  ✅ .env"; else echo "  ❌ .env"; fi
	@if [ -d $(VENV_DIR) ]; then echo "  ✅ venv/"; else echo "  ❌ venv/"; fi
	@if [ -d data ]; then echo "  ✅ data/"; else echo "  ❌ data/"; fi
	@echo ""
	@echo "🐍 Python:"
	@$(PYTHON) --version 2>/dev/null || echo "  ❌ Python не найден"
	@echo ""
	@echo "📦 Зависимости:"
	@if [ -d $(VENV_DIR) ]; then \
		$(VENV_PIP) list 2>/dev/null | grep -E "(aiogram|feedparser|requests)" || echo "  ❌ Зависимости не установлены"; \
	else \
		echo "  ❌ Виртуальное окружение не создано"; \
	fi

# Очистка
clean: ## Очистить временные файлы и кэш
	@echo "$(BLUE)Очистка...$(NC)"
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.log" -delete
	@echo "$(GREEN)✅ Очистка завершена$(NC)"

# Полная очистка (включая venv)
clean-all: clean ## Полная очистка (включая виртуальное окружение)
	@echo "$(BLUE)Полная очистка...$(NC)"
	@rm -rf $(VENV_DIR)
	@rm -f .env
	@rm -rf data
	@echo "$(GREEN)✅ Полная очистка завершена$(NC)"

# Создание резервной копии
backup: ## Создать резервную копию проекта
	@echo "$(BLUE)Создание резервной копии...$(NC)"
	@tar -czf news_bot_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz --exclude='venv' --exclude='*.pyc' --exclude='__pycache__' .
	@echo "$(GREEN)✅ Резервная копия создана$(NC)"

# Просмотр логов
logs: ## Просмотр логов
	@echo "$(BLUE)Просмотр логов...$(NC)"
	@if [ -f logs.txt ]; then \
		tail -f logs.txt; \
	else \
		echo "$(YELLOW)⚠️  Файл логов не найден$(NC)"; \
	fi

# Установка pre-commit хуков
hooks: ## Установить pre-commit хуки
	@echo "$(BLUE)Установка pre-commit хуков...$(NC)"
	@$(VENV_PIP) install pre-commit
	@pre-commit install
	@echo "$(GREEN)✅ Pre-commit хуки установлены$(NC)"

# Форматирование кода
format: ## Форматировать код
	@echo "$(BLUE)Форматирование кода...$(NC)"
	@$(VENV_PIP) install black isort
	@black *.py config/ models/ views/ controllers/ utils/
	@isort *.py config/ models/ views/ controllers/ utils/
	@echo "$(GREEN)✅ Код отформатирован$(NC)"

# Проверка кода
lint: ## Проверить код
	@echo "$(BLUE)Проверка кода...$(NC)"
	@$(VENV_PIP) install flake8 mypy
	@flake8 *.py config/ models/ views/ controllers/ utils/
	@mypy *.py config/ models/ views/ controllers/ utils/
	@echo "$(GREEN)✅ Проверка завершена$(NC)"

# Документация
docs: ## Сгенерировать документацию
	@echo "$(BLUE)Генерация документации...$(NC)"
	@$(VENV_PIP) install sphinx sphinx-rtd-theme
	@echo "$(GREEN)✅ Документация сгенерирована$(NC)"

# Мониторинг
monitor: ## Мониторинг системы
	@echo "$(BLUE)Мониторинг системы...$(NC)"
	@echo "💾 Использование диска:"
	@df -h . | tail -1
	@echo ""
	@echo "🧠 Использование памяти:"
	@free -h 2>/dev/null || vm_stat 2>/dev/null || echo "Недоступно"
	@echo ""
	@echo "📊 Процессы Python:"
	@ps aux | grep python | grep -v grep || echo "Нет активных процессов Python"

# По умолчанию показываем справку
.DEFAULT_GOAL := help
