# 🚀 Руководство по развертыванию

## 📋 Содержание

1. [Подготовка к развертыванию](#подготовка-к-развертыванию)
2. [Развертывание на VPS](#развертывание-на-vps)
3. [Развертывание в Docker](#развертывание-в-docker)
4. [Развертывание на Heroku](#развертывание-на-heroku)
5. [Настройка systemd (Linux)](#настройка-systemd-linux)
6. [Мониторинг и логирование](#мониторинг-и-логирование)
7. [Резервное копирование](#резервное-копирование)
8. [Обновление и откат](#обновление-и-откат)

## Подготовка к развертыванию

### Требования к серверу

**Минимальные требования:**
- **CPU**: 1 ядро
- **RAM**: 512MB
- **Диск**: 1GB свободного места
- **ОС**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+

**Рекомендуемые требования:**
- **CPU**: 2 ядра
- **RAM**: 1GB
- **Диск**: 5GB свободного места
- **ОС**: Ubuntu 22.04 LTS

### Подготовка проекта

```bash
# 1. Клонирование репозитория
git clone <your-repo-url> news_bot
cd news_bot

# 2. Создание production конфигурации
cp env_example.txt .env.production

# 3. Настройка production переменных
nano .env.production
```

### Production конфигурация (.env.production)

```env
# Telegram Bot Token
TELEGRAM_TOKEN=your_production_bot_token

# Пути к данным
DATABASE_PATH=/opt/news_bot/data/news.json
USERS_PATH=/opt/news_bot/data/users.json

# RSS источники
SOURCES=https://feeds.reuters.com/reuters/businessNews,https://feeds.bloomberg.com/markets/news.rss

# Настройки времени
TIMEZONE=Europe/Moscow
DAILY_TIME=09:00

# Production настройки
LOG_LEVEL=INFO
LOG_FILE=/opt/news_bot/logs/bot.log
NEWS_UPDATE_INTERVAL=1800
SCHEDULER_CHECK_INTERVAL=60

# Безопасность
MAX_NEWS_COUNT=5000
FILTER_KEYWORDS=spam,scam,fake
```

## Развертывание на VPS

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y python3.11 python3.11-venv python3.11-dev \
    build-essential git nginx supervisor

# Создание пользователя для бота
sudo useradd -m -s /bin/bash newsbot
sudo usermod -aG sudo newsbot
```

### 2. Установка pyenv (опционально)

```bash
# Переключение на пользователя newsbot
sudo su - newsbot

# Установка pyenv
curl https://pyenv.run | bash

# Добавление в .bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Перезагрузка shell
source ~/.bashrc

# Установка Python
pyenv install 3.11.7
pyenv global 3.11.7
```

### 3. Развертывание приложения

```bash
# Переключение на пользователя newsbot
sudo su - newsbot

# Клонирование проекта
git clone <your-repo-url> /home/newsbot/news_bot
cd /home/newsbot/news_bot

# Создание виртуального окружения
python3.11 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt

# Настройка конфигурации
cp .env.production .env

# Создание директорий
mkdir -p data logs

# Установка прав
chmod +x bot.py
chmod 600 .env
```

### 4. Настройка systemd

```bash
# Создание systemd сервиса
sudo nano /etc/systemd/system/news-bot.service
```

**Содержимое файла /etc/systemd/system/news-bot.service:**

```ini
[Unit]
Description=News Bot - Financial News Aggregator
After=network.target

[Service]
Type=simple
User=newsbot
Group=newsbot
WorkingDirectory=/home/newsbot/news_bot
Environment=PATH=/home/newsbot/news_bot/venv/bin
ExecStart=/home/newsbot/news_bot/venv/bin/python bot.py
Restart=always
RestartSec=10

# Логирование
StandardOutput=journal
StandardError=journal
SyslogIdentifier=news-bot

# Безопасность
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/newsbot/news_bot/data /home/newsbot/news_bot/logs

[Install]
WantedBy=multi-user.target
```

### 5. Запуск сервиса

```bash
# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable news-bot

# Запуск сервиса
sudo systemctl start news-bot

# Проверка статуса
sudo systemctl status news-bot

# Просмотр логов
sudo journalctl -u news-bot -f
```

## Развертывание в Docker

### 1. Создание Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя
RUN useradd -m -s /bin/bash newsbot

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание директорий для данных
RUN mkdir -p data logs && \
    chown -R newsbot:newsbot /app

# Переключение на пользователя newsbot
USER newsbot

# Открытие порта (если нужен)
EXPOSE 8000

# Команда запуска
CMD ["python", "bot.py"]
```

### 2. Создание docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  news-bot:
    build: .
    container_name: news-bot
    restart: unless-stopped
    environment:
      - TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
      - DATABASE_PATH=/app/data/news.json
      - USERS_PATH=/app/data/users.json
      - TIMEZONE=Europe/Moscow
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    env_file:
      - .env.production

  # Опционально: Nginx для мониторинга
  nginx:
    image: nginx:alpine
    container_name: news-bot-nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - news-bot
```

### 3. Запуск в Docker

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f news-bot

# Остановка
docker-compose down

# Обновление
docker-compose pull
docker-compose up -d
```

## Развертывание на Heroku

### 1. Подготовка для Heroku

```bash
# Установка Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Логин в Heroku
heroku login

# Создание приложения
heroku create your-news-bot

# Настройка переменных окружения
heroku config:set TELEGRAM_TOKEN=your_bot_token
heroku config:set TIMEZONE=Europe/Moscow
heroku config:set LOG_LEVEL=INFO
```

### 2. Создание Procfile

```bash
# Procfile
worker: python bot.py
```

### 3. Создание runtime.txt

```bash
# runtime.txt
python-3.11.7
```

### 4. Развертывание

```bash
# Добавление Heroku remote
git remote add heroku https://git.heroku.com/your-news-bot.git

# Развертывание
git push heroku main

# Запуск worker процесса
heroku ps:scale worker=1

# Просмотр логов
heroku logs --tail
```

## Настройка systemd (Linux)

### Создание скрипта управления

```bash
# Создание скрипта управления
sudo nano /usr/local/bin/news-bot-manager
```

**Содержимое скрипта:**

```bash
#!/bin/bash

SERVICE_NAME="news-bot"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
APP_DIR="/home/newsbot/news_bot"
USER="newsbot"

case "$1" in
    start)
        echo "Запуск $SERVICE_NAME..."
        sudo systemctl start $SERVICE_NAME
        ;;
    stop)
        echo "Остановка $SERVICE_NAME..."
        sudo systemctl stop $SERVICE_NAME
        ;;
    restart)
        echo "Перезапуск $SERVICE_NAME..."
        sudo systemctl restart $SERVICE_NAME
        ;;
    status)
        sudo systemctl status $SERVICE_NAME
        ;;
    logs)
        sudo journalctl -u $SERVICE_NAME -f
        ;;
    update)
        echo "Обновление $SERVICE_NAME..."
        cd $APP_DIR
        sudo -u $USER git pull
        sudo -u $USER $APP_DIR/venv/bin/pip install -r requirements.txt
        sudo systemctl restart $SERVICE_NAME
        ;;
    backup)
        echo "Создание резервной копии..."
        sudo -u $USER tar -czf /home/newsbot/backup_$(date +%Y%m%d_%H%M%S).tar.gz -C $APP_DIR data logs
        ;;
    *)
        echo "Использование: $0 {start|stop|restart|status|logs|update|backup}"
        exit 1
        ;;
esac
```

```bash
# Установка прав
sudo chmod +x /usr/local/bin/news-bot-manager

# Использование
news-bot-manager start
news-bot-manager status
news-bot-manager logs
```

## Мониторинг и логирование

### Настройка логирования

```bash
# Создание директории для логов
sudo mkdir -p /var/log/news-bot
sudo chown newsbot:newsbot /var/log/news-bot

# Настройка logrotate
sudo nano /etc/logrotate.d/news-bot
```

**Содержимое /etc/logrotate.d/news-bot:**

```
/var/log/news-bot/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 newsbot newsbot
    postrotate
        systemctl reload news-bot
    endscript
}
```

### Настройка мониторинга

```bash
# Установка htop для мониторинга
sudo apt install htop

# Установка netdata для веб-мониторинга
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
```

### Создание скрипта мониторинга

```bash
# Создание скрипта мониторинга
sudo nano /usr/local/bin/news-bot-monitor
```

**Содержимое скрипта:**

```bash
#!/bin/bash

SERVICE_NAME="news-bot"
LOG_FILE="/var/log/news-bot/monitor.log"

# Проверка статуса сервиса
if ! systemctl is-active --quiet $SERVICE_NAME; then
    echo "$(date): Сервис $SERVICE_NAME не работает. Перезапуск..." >> $LOG_FILE
    systemctl restart $SERVICE_NAME
fi

# Проверка использования диска
DISK_USAGE=$(df /home/newsbot/news_bot | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): Критическое использование диска: ${DISK_USAGE}%" >> $LOG_FILE
fi

# Проверка размера логов
LOG_SIZE=$(du -m /var/log/news-bot | tail -1 | awk '{print $1}')
if [ $LOG_SIZE -gt 100 ]; then
    echo "$(date): Большой размер логов: ${LOG_SIZE}MB" >> $LOG_FILE
fi
```

```bash
# Установка прав
sudo chmod +x /usr/local/bin/news-bot-monitor

# Добавление в crontab
sudo crontab -e
# Добавить строку:
# */5 * * * * /usr/local/bin/news-bot-monitor
```

## Резервное копирование

### Автоматическое резервное копирование

```bash
# Создание скрипта резервного копирования
sudo nano /usr/local/bin/news-bot-backup
```

**Содержимое скрипта:**

```bash
#!/bin/bash

BACKUP_DIR="/home/newsbot/backups"
APP_DIR="/home/newsbot/news_bot"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="news_bot_backup_${DATE}.tar.gz"

# Создание директории для бэкапов
mkdir -p $BACKUP_DIR

# Создание резервной копии
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" \
    -C $APP_DIR \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    .

# Удаление старых бэкапов (старше 7 дней)
find $BACKUP_DIR -name "news_bot_backup_*.tar.gz" -mtime +7 -delete

echo "$(date): Резервная копия создана: ${BACKUP_FILE}"
```

```bash
# Установка прав
sudo chmod +x /usr/local/bin/news-bot-backup

# Добавление в crontab (ежедневно в 2:00)
sudo crontab -e
# Добавить строку:
# 0 2 * * * /usr/local/bin/news-bot-backup
```

### Восстановление из резервной копии

```bash
# Восстановление из резервной копии
sudo systemctl stop news-bot
cd /home/newsbot
tar -xzf backups/news_bot_backup_YYYYMMDD_HHMMSS.tar.gz
sudo systemctl start news-bot
```

## Обновление и откат

### Процедура обновления

```bash
# 1. Создание резервной копии
news-bot-manager backup

# 2. Остановка сервиса
news-bot-manager stop

# 3. Обновление кода
cd /home/newsbot/news_bot
sudo -u newsbot git pull

# 4. Обновление зависимостей
sudo -u newsbot venv/bin/pip install -r requirements.txt

# 5. Запуск сервиса
news-bot-manager start

# 6. Проверка работы
news-bot-manager status
```

### Откат к предыдущей версии

```bash
# 1. Остановка сервиса
news-bot-manager stop

# 2. Откат к предыдущему коммиту
cd /home/newsbot/news_bot
sudo -u newsbot git reset --hard HEAD~1

# 3. Запуск сервиса
news-bot-manager start
```

### Проверка работоспособности

```bash
# Проверка статуса
news-bot-manager status

# Проверка логов
news-bot-manager logs

# Проверка использования ресурсов
htop

# Проверка подключения к Telegram
curl -s "https://api.telegram.org/bot${TELEGRAM_TOKEN}/getMe"
```

---

## 🎉 Готово!

Ваш Telegram-бот-агрегатор финансовых новостей успешно развернут в продакшене!

### Полезные команды:

```bash
# Управление сервисом
news-bot-manager start|stop|restart|status|logs

# Мониторинг
news-bot-manager logs
htop
df -h

# Резервное копирование
news-bot-manager backup

# Обновление
news-bot-manager update
```

### Поддержка:
- 📖 [README.md](README.md) - основная документация
- 🚀 [GETTING_STARTED.md](GETTING_STARTED.md) - руководство по запуску
- 🏗 [ARCHITECTURE.md](ARCHITECTURE.md) - архитектура проекта
- 🚀 [DEPLOYMENT.md](DEPLOYMENT.md) - это руководство

Удачного развертывания! 🚀
