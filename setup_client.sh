#!/bin/bash

# Цветовые коды для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Установка клиента автоматического бронирования      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Проверка Python версии
echo -e "${YELLOW}Проверка версии Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓ Python найден: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 не найден. Установите Python 3.10+${NC}"
    exit 1
fi

# Создание виртуального окружения
echo -e "\n${YELLOW}Создание виртуального окружения...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Виртуальное окружение создано${NC}"
else
    echo -e "${YELLOW}! Виртуальное окружение уже существует${NC}"
fi

# Активация виртуального окружения
echo -e "\n${YELLOW}Активация виртуального окружения...${NC}"
source venv/bin/activate

# Обновление pip
echo -e "\n${YELLOW}Обновление pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ pip обновлен${NC}"

# Установка зависимостей клиента
echo -e "\n${YELLOW}Установка зависимостей клиента...${NC}"
pip install -r requirements-client.txt
echo -e "${GREEN}✓ Зависимости клиента установлены${NC}"

# Создание директорий
echo -e "\n${YELLOW}Создание необходимых директорий...${NC}"
mkdir -p sessions
mkdir -p logs
echo -e "${GREEN}✓ Директории созданы${NC}"

# Проверка конфигурации
echo -e "\n${YELLOW}Проверка конфигурации...${NC}"
if [ ! -f "config.yaml" ]; then
    if [ -f "config.example.yaml" ]; then
        cp config.example.yaml config.yaml
        echo -e "${YELLOW}! Создан config.yaml из примера${NC}"
        echo -e "${YELLOW}! ВАЖНО: Отредактируйте config.yaml перед запуском!${NC}"
    else
        echo -e "${RED}✗ config.example.yaml не найден${NC}"
    fi
else
    echo -e "${GREEN}✓ config.yaml уже существует${NC}"
fi

# Финальное сообщение
echo -e "\n${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Установка завершена успешно!             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Следующие шаги:${NC}"
echo -e "  1. Получите API credentials на ${YELLOW}https://my.telegram.org${NC}"
echo -e "  2. Отредактируйте ${YELLOW}config.yaml${NC} и укажите:"
echo -e "     - api_id и api_hash"
echo -e "     - Ваш номер телефона"
echo -e "     - Username целевого бота"
echo -e "  3. Запустите клиент:"
echo -e "     ${GREEN}source venv/bin/activate${NC}"
echo -e "     ${GREEN}python main.py --mode immediate${NC}  # для тестирования"
echo -e "     или"
echo -e "     ${GREEN}python main.py --mode scheduled${NC}  # для запланированного запуска"
echo ""
echo -e "${YELLOW}Документация: CLIENT_README.md${NC}"
echo ""
