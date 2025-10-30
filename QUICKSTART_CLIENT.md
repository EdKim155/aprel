# Quick Start Guide - Клиент автоматического бронирования

Быстрое руководство по запуску клиента для автоматического бронирования перевозок.

## 🚀 Быстрый старт (5 минут)

### Шаг 1: Установка

```bash
# Запустите автоматическую установку
./setup_client.sh
```

Скрипт автоматически:
- Создаст виртуальное окружение
- Установит все зависимости
- Создаст необходимые директории
- Скопирует пример конфигурации

### Шаг 2: Получение Telegram API credentials

1. Откройте https://my.telegram.org
2. Войдите с номером телефона
3. Перейдите в **"API development tools"**
4. Создайте новое приложение:
   - **App title:** Auto Booking Client
   - **Short name:** booking
   - **Platform:** Desktop
5. Сохраните **api_id** и **api_hash**

### Шаг 3: Настройка конфигурации

```bash
# Отредактируйте config.yaml
nano config.yaml  # или используйте любой редактор
```

Минимальная конфигурация:

```yaml
telegram:
  api_id: 12345678              # ← Ваш API ID
  api_hash: "abc123def456..."   # ← Ваш API hash
  phone: "+79991234567"         # ← Ваш номер телефона

bot:
  username: "your_bot_username" # ← Username бота (без @)
  sms_trigger_text: "Появились новые перевозки"

booking:
  target_time: "11:30:00"       # ← Время бронирования

targets:
  - type: "прямые"
    cities: ["Челябинск", "Екатеринбург"]
    priority: 1

performance:
  polling_interval_ms: 30       # ← Интервал проверки
```

### Шаг 4: Первый запуск

```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Запустите в тестовом режиме
python main.py --mode immediate
```

### Шаг 5: Авторизация

При первом запуске:

```
Enter the code you received: 12345
```

Введите код из Telegram.

Если у вас включена 2FA:

```
Enter your 2FA password: ********
```

**Готово!** Сессия сохранена, повторная авторизация не потребуется.

---

## 📱 Тестирование с ботом

### 1. Запустите бота

В отдельном терминале:

```bash
# Перейдите в директорию проекта
cd /path/to/aprel

# Активируйте окружение бота
source venv/bin/activate

# Запустите бота
python bot.py
```

### 2. Начните диалог с ботом

1. Найдите бота в Telegram
2. Отправьте `/start`
3. Нажмите кнопку **"🧪 Тест"**

### 3. Запустите клиент

```bash
# В другом терминале
source venv/bin/activate
python main.py --mode immediate
```

### 4. Активируйте тест в боте

Нажмите кнопку **"🧪 Тест"** в боте.

**Клиент автоматически:**
1. Обнаружит SMS-уведомление
2. Отправит /start
3. Выберет перевозку
4. Подтвердит бронирование
5. Покажет статистику

### Ожидаемый результат:

```
✅ SMS detected at 15:23:45.047
STAGE 1: Sending /start command...
✅ Stage 1: 47.23ms (SMS → /start)
STAGE 2: Retrieving shipment menu...
Found 4 buttons in menu
STAGE 3: Selecting target shipment...
Selected shipment: Тест_1
✅ Stage 2: 38.45ms (/start → select)
STAGE 4: Confirming booking...
✅ Stage 3: 32.11ms (select → confirm)

🏆 BOOKING COMPLETED in 117.79ms
```

---

## ⏰ Запланированное бронирование

Для автоматического запуска в определенное время:

```bash
# Убедитесь что время в config.yaml установлено правильно
nano config.yaml
# booking.target_time: "11:30:00"

# Запустите в режиме scheduled
python main.py --mode scheduled
```

Программа будет:
1. Ждать до времени подготовки (за 60 сек до цели)
2. Подготовится к мониторингу
3. За 10 секунд начнет интенсивный мониторинг
4. При обнаружении SMS выполнит бронирование

---

## 🔧 Настройка производительности

### Для максимальной скорости:

```yaml
performance:
  polling_interval_ms: 30      # Минимум 30ms (рекомендуется)
  sms_to_start_ms: 50         # Целевое время реакции
  start_to_select_ms: 50      # Целевое время выбора
  select_to_confirm_ms: 30    # Целевое время подтверждения
```

### Для стабильности (если есть ошибки):

```yaml
performance:
  polling_interval_ms: 50      # Увеличить интервал
  max_retries: 5              # Больше попыток
  connection_timeout: 15       # Больший таймаут
```

---

## 🎯 Настройка целевых перевозок

### Пример 1: Один город, высокий приоритет

```yaml
targets:
  - type: "прямые"
    cities: ["Москва"]
    priority: 1
```

### Пример 2: Несколько городов с приоритетами

```yaml
targets:
  - type: "прямые"
    cities: ["Челябинск", "Екатеринбург"]
    priority: 1
    
  - type: "прямые"
    cities: ["Тюмень", "Омск"]
    priority: 2
    
  - type: "магистральные"
    cities: ["Москва", "Казань"]
    priority: 3
```

Клиент будет искать в порядке приоритета (1 → 2 → 3).

---

## 📊 Просмотр логов

### Последние логи:

```bash
tail -f logs/booking_client.log
```

### JSON логи для анализа:

```bash
cat logs/booking_client_json.log | jq
```

### Поиск ошибок:

```bash
grep ERROR logs/booking_client.log
```

---

## ❓ Частые проблемы

### 1. "Failed to initialize client"

**Причина:** Неверные API credentials

**Решение:**
- Проверьте api_id и api_hash в config.yaml
- Убедитесь что credentials получены с my.telegram.org

### 2. "Bot not found"

**Причина:** Неправильный username бота

**Решение:**
- Username указывается БЕЗ символа @
- Убедитесь что вы начали диалог с ботом (отправьте /start вручную)

### 3. "SMS not detected"

**Причина:** Текст SMS не совпадает с настройкой

**Решение:**
- Проверьте `bot.sms_trigger_text` в config.yaml
- Должно быть: "Появились новые перевозки"

### 4. "FloodWaitError"

**Причина:** Слишком много запросов к Telegram

**Решение:**
- Увеличьте `polling_interval_ms` до 50-100ms
- Подождите указанное время
- Перезапустите клиент

### 5. "Session file not found"

**Причина:** Первый запуск или удалена сессия

**Решение:**
- Это нормально! Просто авторизуйтесь заново
- Введите код из Telegram

---

## 🔐 Безопасность

### Что НЕ делать:

❌ Не публикуйте `config.yaml` в git  
❌ Не делитесь файлами из `sessions/`  
❌ Не передавайте API credentials другим  
❌ Не используйте для спама или абуза

### Что делать:

✅ Храните config.yaml локально  
✅ Добавьте `config.yaml` в .gitignore (уже добавлено)  
✅ Регулярно делайте backup сессий  
✅ Используйте только для своих ботов

---

## 🆘 Получение помощи

### 1. Проверьте документацию

- `CLIENT_README.md` - Полное руководство
- `CLIENT_ARCHITECTURE.md` - Техническая архитектура
- `QUICKSTART_CLIENT.md` - Этот файл

### 2. Запустите тесты

```bash
python test_client.py
```

### 3. Проверьте логи

```bash
tail -100 logs/booking_client.log
```

### 4. Создайте issue

Если проблема не решена, создайте issue с:
- Описанием проблемы
- Версией Python (`python --version`)
- Логами (`logs/booking_client.log`)
- Конфигурацией (без credentials!)

---

## 🎓 Дополнительное обучение

### Рекомендуемые ресурсы:

1. **Telegram Client API**
   - https://docs.telethon.dev/
   - https://core.telegram.org/

2. **Python asyncio**
   - https://docs.python.org/3/library/asyncio.html

3. **Optimization techniques**
   - Профилирование с `cProfile`
   - Мониторинг с `top`, `htop`

---

## 🚀 Что дальше?

После успешного тестирования:

1. **Настройте расписание** для автоматического запуска
2. **Оптимизируйте параметры** для вашей сети
3. **Настройте уведомления** в Telegram
4. **Добавьте мониторинг** логов
5. **Создайте резервные копии** сессий

---

**Готово! Теперь вы можете использовать клиент для автоматического бронирования.**

Удачи! 🎉
