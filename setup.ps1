# 🚀 Скрипт автоматической настройки проекта для Windows
# Telegram-бот-агрегатор финансовых новостей

param(
    [switch]$SkipPyenv,
    [switch]$SkipVenv,
    [switch]$SkipDependencies
)

# Функции для вывода сообщений
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Проверка PowerShell версии
function Test-PowerShellVersion {
    Write-Info "Проверка версии PowerShell..."
    
    $version = $PSVersionTable.PSVersion
    if ($version.Major -lt 5) {
        Write-Error "Требуется PowerShell 5.0 или новее. Текущая версия: $version"
        exit 1
    }
    
    Write-Success "PowerShell версия: $version"
}

# Проверка наличия Python
function Test-Python {
    Write-Info "Проверка наличия Python..."
    
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python найден: $pythonVersion"
            return $true
        }
    }
    catch {
        Write-Warning "Python не найден в PATH"
    }
    
    return $false
}

# Установка Python через winget
function Install-Python {
    Write-Info "Установка Python через winget..."
    
    try {
        # Проверка наличия winget
        winget --version | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Info "Установка Python 3.11..."
            winget install Python.Python.3.11
            Write-Success "Python установлен"
        } else {
            Write-Error "winget не найден. Установите Python вручную с https://python.org"
            exit 1
        }
    }
    catch {
        Write-Error "Ошибка установки Python. Установите вручную с https://python.org"
        exit 1
    }
}

# Создание виртуального окружения
function New-VirtualEnvironment {
    Write-Info "Создание виртуального окружения..."
    
    if (Test-Path "venv") {
        Write-Warning "Виртуальное окружение уже существует. Удаление..."
        Remove-Item -Recurse -Force "venv"
    }
    
    python -m venv venv
    Write-Success "Виртуальное окружение создано"
}

# Активация виртуального окружения
function Enable-VirtualEnvironment {
    Write-Info "Активация виртуального окружения..."
    
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & "venv\Scripts\Activate.ps1"
        Write-Success "Виртуальное окружение активировано"
    } else {
        Write-Error "Не удалось активировать виртуальное окружение"
        exit 1
    }
}

# Установка зависимостей
function Install-Dependencies {
    Write-Info "Установка зависимостей..."
    
    # Обновление pip
    python -m pip install --upgrade pip
    
    # Установка зависимостей
    pip install -r requirements.txt
    
    Write-Success "Зависимости установлены"
}

# Настройка конфигурации
function Set-Configuration {
    Write-Info "Настройка конфигурации..."
    
    if (-not (Test-Path ".env")) {
        if (Test-Path "env_example.txt") {
            Copy-Item "env_example.txt" ".env"
            Write-Success "Файл .env создан из примера"
        } else {
            Write-Error "Файл env_example.txt не найден"
            exit 1
        }
    } else {
        Write-Warning "Файл .env уже существует"
    }
    
    # Создание директорий для данных
    if (-not (Test-Path "data")) {
        New-Item -ItemType Directory -Path "data"
        Write-Success "Директория data создана"
    }
}

# Проверка конфигурации
function Test-Configuration {
    Write-Info "Проверка конфигурации..."
    
    if (-not (Test-Path ".env")) {
        Write-Error "Файл .env не найден"
        exit 1
    }
    
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "TELEGRAM_TOKEN=your_bot_token_here") {
        Write-Warning "Токен бота не настроен. Необходимо отредактировать .env файл"
    } else {
        Write-Success "Токен бота настроен"
    }
}

# Тестирование установки
function Test-Installation {
    Write-Info "Тестирование установки..."
    
    # Проверка Python
    $pythonVersion = python --version
    Write-Success "Python: $pythonVersion"
    
    # Проверка pip
    $pipVersion = pip --version
    Write-Success "Pip: $pipVersion"
    
    # Проверка импортов
    try {
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
        Write-Success "Тестирование завершено успешно"
    }
    catch {
        Write-Error "Ошибка при тестировании импортов"
        exit 1
    }
}

# Вывод инструкций
function Show-Instructions {
    Write-Info "Настройка завершена!"
    Write-Host ""
    Write-Host "🎉 Проект готов к запуску!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Следующие шаги:" -ForegroundColor Yellow
    Write-Host "1. Отредактируйте файл .env и добавьте токен бота:"
    Write-Host "   notepad .env"
    Write-Host ""
    Write-Host "2. Активируйте виртуальное окружение:"
    Write-Host "   .\venv\Scripts\Activate.ps1"
    Write-Host ""
    Write-Host "3. Запустите бота:"
    Write-Host "   python bot.py"
    Write-Host ""
    Write-Host "Дополнительная информация:" -ForegroundColor Blue
    Write-Host "• README.md - основная документация"
    Write-Host "• GETTING_STARTED.md - подробное руководство"
    Write-Host "• ARCHITECTURE.md - архитектура проекта"
    Write-Host ""
    Write-Host "Удачного использования! 🚀" -ForegroundColor Green
}

# Основная функция
function Main {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
    Write-Host "║              🚀 Настройка Telegram-бота                     ║" -ForegroundColor Blue
    Write-Host "║              Агрегатор финансовых новостей                  ║" -ForegroundColor Blue
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
    Write-Host ""
    
    Test-PowerShellVersion
    
    if (-not $SkipPyenv) {
        if (-not (Test-Python)) {
            Install-Python
        }
    }
    
    if (-not $SkipVenv) {
        New-VirtualEnvironment
        Enable-VirtualEnvironment
    }
    
    if (-not $SkipDependencies) {
        Install-Dependencies
    }
    
    Set-Configuration
    Test-Configuration
    Test-Installation
    Show-Instructions
}

# Запуск скрипта
Main
