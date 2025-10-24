# 🚀 Руководство по запуску проекта

## 📋 Содержание

1. [Предварительные требования](#предварительные-требования)
2. [Установка pyenv](#установка-pyenv)
3. [Установка Python](#установка-python)
4. [Создание виртуального окружения](#создание-виртуального-окружения)
5. [Установка зависимостей](#установка-зависимостей)
6. [Настройка конфигурации](#настройка-конфигурации)
7. [Создание Telegram-бота](#создание-telegram-бота)
8. [Запуск проекта](#запуск-проекта)
9. [Проверка работы](#проверка-работы)
10. [Устранение неполадок](#устранение-неполадок)

## Предварительные требования

### Системные требования
- **macOS**: 10.15+ (Catalina или новее)
- **Linux**: Ubuntu 18.04+ или аналогичный дистрибутив
- **Windows**: Windows 10+ с WSL2 (рекомендуется)
- **RAM**: минимум 2GB, рекомендуется 4GB+
- **Дисковое пространство**: минимум 1GB свободного места

### Необходимые инструменты
- Git
- curl или wget
- Компилятор C (для сборки Python)

## Установка pyenv

### macOS

```bash
# Установка через Homebrew (рекомендуется)
brew install pyenv

# Или через curl
curl https://pyenv.run | bash
```

### Linux (Ubuntu/Debian)

```bash
# Установка зависимостей
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
    libffi-dev liblzma-dev

# Установка pyenv
curl https://pyenv.run | bash

# Добавление в .bashrc или .zshrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Перезагрузка shell
source ~/.bashrc
```

### Windows (WSL2)

```bash
# В WSL2 выполните команды для Linux
curl https://pyenv.run | bash

# Добавление в .bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

source ~/.bashrc
```

### Проверка установки pyenv

```bash
pyenv --version
# Должно показать версию pyenv, например: pyenv 2.3.0
```

## Установка Python

### Рекомендуемая версия Python

Проект протестирован на Python 3.11.x. Рекомендуется использовать Python 3.11.0 или новее.

```bash
# Просмотр доступных версий Python
pyenv install --list | grep "3.11"

# Установка Python 3.11.7 (рекомендуемая версия)
pyenv install 3.11.7

# Установка Python 3.11.0 (минимальная версия)
pyenv install 3.11.0

# Установка последней стабильной версии 3.11
pyenv install 3.11
```

### Настройка глобальной версии Python

```bash
# Установка Python 3.11.7 как глобальной версии
pyenv global 3.11.7

# Проверка версии Python
python --version
# Должно показать: Python 3.11.7

# Проверка версии pip
pip --version
# Должно показать версию pip для Python 3.11
```

## Создание виртуального окружения

### Переход в директорию проекта

```bash
# Переход в директорию проекта
cd /path/to/news_bot

# Или если вы находитесь в родительской директории
cd news_bot
```

### Создание виртуального окружения

```bash
# Создание виртуального окружения с Python 3.11
python -m venv venv

# Активация виртуального окружения

# На macOS/Linux:
source venv/bin/activate

# На Windows (PowerShell):
# venv\Scripts\Activate.ps1

# На Windows (Command Prompt):
# venv\Scripts\activate.bat
```

### Проверка активации виртуального окружения

После активации в командной строке должно появиться `(venv)`:

```bash
# Проверка Python
which python
# Должно показать путь к Python в виртуальном окружении

# Проверка pip
which pip
# Должно показать путь к pip в виртуальном окружении

# Проверка версии Python
python --version
# Должно показать: Python 3.11.7
```

## Установка зависимостей

### Обновление pip

```bash
# Обновление pip до последней версии
python -m pip install --upgrade pip
```

### Установка зависимостей проекта

```bash
# Установка всех зависимостей из requirements.txt
pip install -r requirements.txt
```

### Проверка установленных пакетов

```bash
# Просмотр установленных пакетов
pip list

# Должны быть установлены:
# aiogram==3.1.1
# feedparser==6.0.10
# python-dotenv==1.0.0
# requests==2.31.0
# beautifulsoup4==4.12.2
# lxml==4.9.3
# schedule==1.2.0
# pytz==2023.3
```

## Настройка конфигурации

### Создание файла конфигурации

```bash
# Копирование примера конфигурации
cp env_example.txt .env

# Редактирование файла конфигурации
nano .env
# или
vim .env
# или откройте в любом текстовом редакторе
```

### Настройка переменных окружения

Отредактируйте файл `.env`:

```env
# Telegram Bot Token (получить у @BotFather)
TELEGRAM_TOKEN=your_bot_token_here

# Путь к базе данных новостей
DATABASE_PATH=data/news.json

# Путь к базе данных пользователей
USERS_PATH=data/users.json

# RSS источники новостей (разделенные запятыми)
SOURCES=https://feeds.reuters.com/reuters/businessNews,https://feeds.bloomberg.com/markets/news.rss,https://feeds.finance.yahoo.com/rss/2.0/headline

# Часовой пояс для отправки дайджестов
TIMEZONE=Europe/Moscow

# Время отправки ежедневного дайджеста (формат: HH:MM)
DAILY_TIME=09:00

# Количество новостей в дайджесте
DIGEST_SIZE=5

# Ключевые слова для фильтрации (разделенные запятыми)
FILTER_KEYWORDS=криптовалюта,IPO,ICO

# Максимальное количество новостей для хранения
MAX_NEWS_COUNT=1000

# Настройки логирования
LOG_LEVEL=INFO
LOG_FILE=logs.txt

# Интервалы обновления (в секундах)
NEWS_UPDATE_INTERVAL=1800
SCHEDULER_CHECK_INTERVAL=60
```

## Создание Telegram-бота

### Получение токена бота

1. **Откройте Telegram** и найдите [@BotFather](https://t.me/BotFather)

2. **Отправьте команду** `/newbot`

3. **Введите имя бота** (например: "Financial News Bot")

4. **Введите username бота** (например: "financial_news_bot")

5. **Скопируйте токен** (выглядит как: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

6. **Вставьте токен в .env файл**:
   ```env
   TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### Настройка команд бота (опционально)

Отправьте BotFather команду `/setcommands` и выберите вашего бота, затем отправьте:

```
start - Приветствие и описание функционала
help - Показать все команды
addtopic - Добавить новую тему
removetopic - Удалить тему
mytopics - Показать список подписанных тем
latest - Показать последние новости
search - Найти новости по ключевым словам
favorites - Показать сохранённые материалы
save - Сохранить новость в избранное
```

## Запуск проекта

### Проверка структуры проекта

```bash
# Проверка структуры файлов
ls -la

# Должны быть видны:
# bot.py
# requirements.txt
# .env
# config/
# models/
# views/
# controllers/
# utils/
# data/
```

### Запуск бота

```bash
# Убедитесь, что виртуальное окружение активировано
# (в командной строке должно быть (venv))

# Запуск бота
python bot.py
```

### Ожидаемый вывод при запуске

```
2024-01-15 10:30:00 - __main__ - INFO - Запуск бота...
2024-01-15 10:30:00 - __main__ - INFO - Статус бота: {'initialized': True, 'news_count': 0, 'users_count': 0, 'scheduler_running': True}
2024-01-15 10:30:00 - __main__ - INFO - Планировщик задач настроен
2024-01-15 10:30:00 - __main__ - INFO - Бот успешно инициализирован
2024-01-15 10:30:00 - __main__ - INFO - Запуск бота...
2024-01-15 10:30:00 - __main__ - INFO - Планировщик запущен
```

## Проверка работы

### Тестирование команд бота

1. **Найдите вашего бота** в Telegram по username
2. **Отправьте команду** `/start`
3. **Проверьте ответ** - должно прийти приветственное сообщение
4. **Попробуйте другие команды**:
   - `/help` - справка
   - `/addtopic экономика` - добавить тему
   - `/mytopics` - показать темы
   - `/latest` - последние новости

### Проверка логов

```bash
# Просмотр логов в реальном времени
tail -f logs.txt

# Просмотр последних 50 строк логов
tail -n 50 logs.txt
```

### Проверка данных

```bash
# Проверка базы данных новостей
cat data/news.json

# Проверка базы данных пользователей
cat data/users.json
```

## Устранение неполадок

### Проблемы с pyenv

```bash
# Если pyenv не найден после установки
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

# Проверка установки
pyenv --version
```

### Проблемы с виртуальным окружением

```bash
# Деактивация текущего окружения
deactivate

# Удаление старого окружения
rm -rf venv

# Создание нового окружения
python -m venv venv
source venv/bin/activate

# Переустановка зависимостей
pip install -r requirements.txt
```

### Проблемы с зависимостями

```bash
# Обновление pip
python -m pip install --upgrade pip

# Установка зависимостей по одной
pip install aiogram==3.1.1
pip install feedparser==6.0.10
pip install python-dotenv==1.0.0
# и т.д.

# Проверка установленных пакетов
pip list
```

### Проблемы с токеном бота

```bash
# Проверка файла .env
cat .env | grep TELEGRAM_TOKEN

# Должно показать:
# TELEGRAM_TOKEN=ваш_токен_здесь

# Если токен не установлен, отредактируйте .env файл
nano .env
```

### Проблемы с правами доступа

```bash
# Установка прав на выполнение
chmod +x bot.py

# Установка прав на директории
chmod -R 755 data/
chmod -R 755 config/
chmod -R 755 models/
chmod -R 755 views/
chmod -R 755 controllers/
chmod -R 755 utils/
```

### Проблемы с портами (если есть)

```bash
# Проверка использования портов
netstat -tulpn | grep :8080

# Если порт занят, найдите процесс и завершите его
sudo kill -9 PID_ПРОЦЕССА
```

## Дополнительные команды

### Деактивация виртуального окружения

```bash
# Деактивация виртуального окружения
deactivate

# После деактивации (venv) исчезнет из командной строки
```

### Обновление зависимостей

```bash
# Активация виртуального окружения
source venv/bin/activate

# Обновление всех зависимостей
pip install --upgrade -r requirements.txt

# Обновление конкретной зависимости
pip install --upgrade aiogram
```

### Создание резервной копии

```bash
# Создание архива проекта
tar -czf news_bot_backup_$(date +%Y%m%d).tar.gz news_bot/

# Исключение виртуального окружения из архива
tar -czf news_bot_backup_$(date +%Y%m%d).tar.gz --exclude='venv' news_bot/
```

## Полезные команды для разработки

### Запуск в режиме отладки

```bash
# Установка переменной окружения для отладки
export LOG_LEVEL=DEBUG

# Запуск бота
python bot.py
```

### Просмотр структуры проекта

```bash
# Древовидная структура (если установлен tree)
tree -a

# Или через find
find . -type f -name "*.py" | sort
```

### Очистка кэша Python

```bash
# Удаление файлов .pyc
find . -name "*.pyc" -delete

# Удаление директорий __pycache__
find . -name "__pycache__" -type d -exec rm -rf {} +
```

---

## 🎉 Готово!

Теперь ваш Telegram-бот-агрегатор финансовых новостей готов к работе! 

### Следующие шаги:
1. Протестируйте все команды бота
2. Настройте дополнительные RSS-источники
3. Добавьте новых пользователей
4. Настройте время отправки дайджестов под ваши нужды

### Поддержка:
- 📖 [README.md](README.md) - основная документация
- 🏗 [ARCHITECTURE.md](ARCHITECTURE.md) - архитектура проекта
- 🚀 [GETTING_STARTED.md](GETTING_STARTED.md) - это руководство

Удачного использования! 🚀
