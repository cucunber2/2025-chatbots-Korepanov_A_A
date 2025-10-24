#!/bin/bash

# 🚀 Скрипт автоматической настройки проекта
# Telegram-бот-агрегатор финансовых новостей

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
print_message() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка операционной системы
check_os() {
    print_message "Проверка операционной системы..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "Обнаружена macOS"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "Обнаружен Linux"
    else
        print_error "Неподдерживаемая операционная система: $OSTYPE"
        exit 1
    fi
}

# Проверка наличия pyenv
check_pyenv() {
    print_message "Проверка наличия pyenv..."
    
    if command -v pyenv &> /dev/null; then
        print_success "pyenv уже установлен: $(pyenv --version)"
    else
        print_warning "pyenv не найден. Установка..."
        install_pyenv
    fi
}

# Установка pyenv
install_pyenv() {
    print_message "Установка pyenv..."
    
    if [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            print_message "Установка через Homebrew..."
            brew install pyenv
        else
            print_message "Установка через curl..."
            curl https://pyenv.run | bash
        fi
    elif [[ "$OS" == "linux" ]]; then
        print_message "Установка зависимостей для Linux..."
        sudo apt update
        sudo apt install -y make build-essential libssl-dev zlib1g-dev \
            libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
            libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
            libffi-dev liblzma-dev
        
        print_message "Установка pyenv..."
        curl https://pyenv.run | bash
    fi
    
    # Добавление pyenv в shell конфигурацию
    if ! grep -q "pyenv" ~/.bashrc; then
        print_message "Добавление pyenv в ~/.bashrc..."
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
        echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
        echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    fi
    
    # Загрузка pyenv в текущую сессию
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    
    print_success "pyenv установлен: $(pyenv --version)"
}

# Установка Python
install_python() {
    install_python() {
    print_message "Установка Python 3.11.7..."
    
    if pyenv versions | grep -q "3.11.7"; then
        print_success "Python 3.11.7 уже установлен"
    else
        print_message "Установка Python 3.11.7 (это может занять несколько минут)..."
        pyenv install 3.11.7
    fi

    pyenv global 3.11.7

    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
    hash -r

    print_success "Python 3.11.7 установлен как глобальная версия"
}
}

# Создание виртуального окружения
create_venv() {
    print_message "Создание виртуального окружения..."
    
    if [ -d "venv" ]; then
        print_warning "Виртуальное окружение уже существует. Удаление..."
        rm -rf venv
    fi

    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    hash -r
    
    python -m venv venv
    print_success "Виртуальное окружение создано"
}

# Активация виртуального окружения
activate_venv() {
    print_message "Активация виртуального окружения..."
    source venv/bin/activate
    print_success "Виртуальное окружение активировано"
}

# Установка зависимостей
install_dependencies() {
    print_message "Установка зависимостей..."
    
    # Обновление pip
    python -m pip install --upgrade pip
    
    # Установка зависимостей
    pip install -r requirements.txt
    
    print_success "Зависимости установлены"
}

# Создание конфигурации
setup_config() {
    print_message "Настройка конфигурации..."
    
    if [ ! -f ".env" ]; then
        if [ -f "env_example.txt" ]; then
            cp env_example.txt .env
            print_success "Файл .env создан из примера"
        else
            print_error "Файл env_example.txt не найден"
            exit 1
        fi
    else
        print_warning "Файл .env уже существует"
    fi
    
    # Создание директорий для данных
    mkdir -p data
    print_success "Директории для данных созданы"
}

# Проверка конфигурации
check_config() {
    print_message "Проверка конфигурации..."
    
    if [ ! -f ".env" ]; then
        print_error "Файл .env не найден"
        exit 1
    fi
    
    # Проверка токена бота
    if ! grep -q "TELEGRAM_TOKEN=your_bot_token_here" .env; then
        print_success "Токен бота настроен"
    else
        print_warning "Токен бота не настроен. Необходимо отредактировать .env файл"
    fi
}

# Тестирование установки
test_installation() {
    print_message "Тестирование установки..."
    
    # Проверка Python
    python_version=$(python --version)
    print_success "Python: $python_version"
    
    # Проверка pip
    pip_version=$(pip --version)
    print_success "Pip: $pip_version"
    
    # Проверка импортов
    python -c "
import sys
try:
    import aiogram
    import feedparser
    import requests
    import schedule
    print('✅ Все основные зависимости импортированы успешно')
except ImportError as e:
    print(f'❌ Ошибка импорта: {e}')
    sys.exit(1)
"
    
    print_success "Тестирование завершено успешно"
}

# Вывод инструкций
show_instructions() {
    print_message "Настройка завершена!"
    echo
    echo -e "${GREEN}🎉 Проект готов к запуску!${NC}"
    echo
    echo -e "${YELLOW}Следующие шаги:${NC}"
    echo "1. Отредактируйте файл .env и добавьте токен бота:"
    echo "   nano .env"
    echo
    echo "2. Активируйте виртуальное окружение:"
    echo "   source venv/bin/activate"
    echo
    echo "3. Запустите бота:"
    echo "   python bot.py"
    echo
    echo -e "${BLUE}Дополнительная информация:${NC}"
    echo "• README.md - основная документация"
    echo "• GETTING_STARTED.md - подробное руководство"
    echo "• ARCHITECTURE.md - архитектура проекта"
    echo
    echo -e "${GREEN}Удачного использования! 🚀${NC}"
}

# Основная функция
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              🚀 Настройка Telegram-бота                     ║"
    echo "║              Агрегатор финансовых новостей                  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    check_os
    check_pyenv
    install_python
    create_venv
    activate_venv
    install_dependencies
    setup_config
    check_config
    test_installation
    show_instructions
}

# Запуск скрипта
main "$@"
