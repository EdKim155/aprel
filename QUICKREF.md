# Краткая справка

## 🚀 Быстрый старт

```bash
# 1. Создать .env файл
cp .env.example .env

# 2. Отредактировать .env (добавить токен и admin ID)
nano .env

# 3. Установить зависимости
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Запустить бота
python bot.py
```

## 📝 Основные команды

### Пользовательские команды
- `/start` - Запуск бота

### Админские команды
- `/admin_reset` - Сброс бронирований
- `/admin_stats` - Статистика
- `/admin_logs [user_id]` - Логи пользователя
- `/admin_test_stats` - Статистика тестов
- `/admin_add_shipment [type] [city] [qty]` - Добавить перевозку
- `/admin_trigger_sms` - Отправить SMS всем
- `/open_booking` - Открыть бронирование

## 🔧 Настройка

### .env файл
```env
BOT_TOKEN=ваш_токен_от_BotFather
ADMIN_IDS=123456789
BOOKING_TIME=11:30
```

### Изменить перевозки по умолчанию
Отредактируйте `config.py` → `DEFAULT_SHIPMENTS`

### Изменить тестовые перевозки
Отредактируйте `config.py` → `TEST_SHIPMENTS`

## 📊 Проверка работы

### Проверить импорты
```bash
python3 test_import.py
```

### Проверить все файлы
```bash
python3 verify_project.py
```

### Проверить базу данных
```bash
sqlite3 bot.db "SELECT * FROM users;"
sqlite3 bot.db "SELECT * FROM shipments;"
```

## 🐳 Docker

### Запуск через Docker Compose
```bash
docker-compose up -d
```

### Просмотр логов
```bash
docker-compose logs -f
```

### Остановка
```bash
docker-compose down
```

## 🔍 Отладка

### Просмотр логов бота
```bash
# Если запущен в терминале - логи видны сразу

# Если через systemd:
sudo journalctl -u booking-bot -f

# Если через docker:
docker-compose logs -f bot
```

### Проверка БД
```bash
sqlite3 bot.db
> .tables
> SELECT COUNT(*) FROM users;
> SELECT * FROM shipments WHERE is_booked = 1;
> .quit
```

### Сброс БД
```bash
rm bot.db
# При следующем запуске создастся новая
```

## 📁 Структура файлов

| Файл | Описание |
|------|----------|
| `bot.py` | Главный файл бота |
| `config.py` | Конфигурация |
| `database.py` | База данных |
| `keyboards.py` | Клавиатуры |
| `utils.py` | Утилиты |

## 📚 Документация

- `README.md` - Основная документация
- `SETUP.md` - Установка и настройка
- `TESTING.md` - Руководство по тестированию
- `ARCHITECTURE.md` - Архитектура проекта
- `CHANGELOG.md` - История изменений
- `PROJECT_SUMMARY.md` - Сводка проекта
- `QUICKREF.md` - Эта справка

## 🎯 Основные функции

### Главное меню (5 кнопок)
1. Список прямых перевозок
2. Список магистральных перевозок
3. Мои перевозки
4. Настройки
5. 🧪 Тест

### Процесс бронирования
1. Выбрать тип перевозки
2. Выбрать конкретную перевозку
3. Нажать "✅ Подтвердить"
4. Получить результат с временем обработки

### Режим тестирования
1. Нажать "🧪 Тест"
2. Дождаться SMS
3. Нажать `/start`
4. Выбрать тестовую перевозку
5. Получить результаты:
   - Время от SMS до /start
   - Время от /start до выбора
   - Общее время

## ⚠️ Важные замечания

### Токен бота
- Получите у @BotFather
- Храните в `.env` файле
- Не коммитьте в git

### Admin ID
- Получите у @userinfobot
- Укажите в `.env` файле
- Можно несколько через запятую

### Изображение логотипа
- Имя файла: `5445047061721511293.jpg`
- Необязательно (бот работает без него)
- Положите в корень проекта

### База данных
- Создается автоматически
- Файл: `bot.db`
- SQLite (не нужен отдельный сервер)

## 🆘 Решение проблем

### Бот не запускается
```bash
# Проверить версию Python
python3 --version  # должна быть 3.10+

# Проверить зависимости
pip list

# Проверить .env файл
cat .env
```

### Бот не отвечает
- Проверить токен в `.env`
- Проверить интернет-соединение
- Посмотреть логи

### Админские команды не работают
- Проверить Admin ID в `.env`
- Перезапустить бота после изменения `.env`

### База данных поломалась
```bash
# Сделать бэкап (если нужно)
cp bot.db bot.db.backup

# Удалить и пересоздать
rm bot.db
python bot.py  # создаст новую БД
```

## 📞 Получить помощь

1. Прочитайте `README.md`
2. Прочитайте `SETUP.md`
3. Прочитайте `TESTING.md`
4. Проверьте логи бота

## 🔗 Полезные ссылки

- Telegram Bot API: https://core.telegram.org/bots/api
- aiogram: https://docs.aiogram.dev/
- Python asyncio: https://docs.python.org/3/library/asyncio.html

## 📊 Команды для разработки

```bash
# Активировать venv
source venv/bin/activate

# Деактивировать venv
deactivate

# Обновить зависимости
pip install -r requirements.txt --upgrade

# Проверить синтаксис
python3 -m py_compile bot.py

# Запустить бота
python bot.py

# Запустить в фоне
nohup python bot.py > bot.log 2>&1 &

# Остановить фоновый процесс
ps aux | grep bot.py
kill [PID]
```

## ✅ Checklist перед запуском

- [ ] Python 3.10+ установлен
- [ ] Создан .env файл
- [ ] BOT_TOKEN указан в .env
- [ ] ADMIN_IDS указан в .env
- [ ] Зависимости установлены (pip install -r requirements.txt)
- [ ] Тестовый импорт прошел (python3 test_import.py)
- [ ] Проверка проекта прошла (python3 verify_project.py)
- [ ] Бот запущен (python bot.py)
- [ ] Бот отвечает на /start

## 🎉 Готово!

Если все пункты checklist выполнены - бот готов к работе!
