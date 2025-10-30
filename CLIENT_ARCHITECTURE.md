# Архитектура клиента автоматического бронирования

## Обзор системы

Клиентское приложение разработано для автоматизации процесса бронирования перевозок через Telegram-ботов с минимальной задержкой. Использует Telegram Client API (MTProto) для имитации действий пользователя.

## Архитектурные принципы

### 1. Модульность
Система разделена на независимые модули с четкой ответственностью:
- **Core** - основная логика работы с Telegram
- **Config** - управление конфигурацией и сессиями
- **Utils** - вспомогательные утилиты (логирование, метрики, уведомления)

### 2. Асинхронность
Все операции выполняются асинхронно с использованием `asyncio` для:
- Минимизации задержек
- Параллельной обработки задач
- Эффективного использования ресурсов

### 3. Производительность
Оптимизации для достижения целевого времени < 150ms:
- Прямые вызовы Telegram API без промежуточных слоев
- Предварительное кэширование данных
- Минимальные задержки между операциями (15ms)
- Polling с интервалом 30ms

## Структура модулей

```
auto_booking/
├── __init__.py           # Экспорт основных компонентов
│
├── core/                 # Ядро системы
│   ├── __init__.py
│   ├── client.py         # Telegram клиент (Telethon)
│   ├── bot_handler.py    # Обработка сообщений и мониторинг
│   ├── button_clicker.py # Логика нажатия кнопок
│   └── scheduler.py      # Планировщик задач
│
├── config/               # Конфигурация
│   ├── __init__.py
│   ├── settings.py       # Загрузка и валидация настроек
│   └── session_manager.py # Управление Telegram сессиями
│
└── utils/                # Утилиты
    ├── __init__.py
    ├── logger.py         # Продвинутое логирование (Loguru)
    ├── metrics.py        # Сбор метрик производительности
    └── notifier.py       # Уведомления пользователя
```

## Компоненты системы

### Core модули

#### 1. BookingClient (client.py)

**Назначение:** Обертка над Telegram Client для работы с MTProto API

**Основные методы:**
- `initialize()` - Инициализация и авторизация клиента
- `send_message()` - Отправка сообщений с измерением времени
- `get_latest_messages()` - Получение последних сообщений
- `is_connected()` - Проверка соединения

**Особенности:**
- Автоматическое переподключение при разрыве связи
- Обработка 2FA авторизации
- Сохранение сессии для повторного использования
- Интегрированный сбор метрик

**Зависимости:**
- Telethon
- MetricsCollector

#### 2. BotHandler (bot_handler.py)

**Назначение:** Мониторинг сообщений от бота и выполнение последовательности бронирования

**Основные методы:**
- `monitor_sms()` - Мониторинг SMS-уведомлений с низкой задержкой
- `execute_booking_sequence()` - Полная последовательность бронирования
- `is_sms_notification()` - Определение SMS-сообщений

**Алгоритм работы:**

```
1. Мониторинг (каждые 30ms)
   ↓
2. Обнаружение SMS
   ↓
3. Отправка /start (< 50ms)
   ↓
4. Получение меню с перевозками
   ↓
5. Выбор целевой перевозки (< 50ms)
   ↓
6. Получение сообщения с подтверждением
   ↓
7. Клик "Подтвердить" (< 30ms)
   ↓
8. Получение результата
```

**Метрики:**
- `sms_to_start_ms` - Время от SMS до /start
- `start_to_select_ms` - Время от /start до выбора
- `select_to_confirm_ms` - Время от выбора до подтверждения
- `total_time_ms` - Общее время

#### 3. ButtonClicker (button_clicker.py)

**Назначение:** Ультра-быстрое нажатие inline-кнопок

**Основные методы:**
- `ultra_fast_click()` - Прямой вызов GetBotCallbackAnswerRequest
- `find_button_by_text()` - Поиск кнопки по тексту
- `find_button_by_pattern()` - Поиск по нескольким паттернам
- `click_confirm_button()` - Специальная обработка кнопки подтверждения

**Оптимизации:**
- Использование `time.perf_counter()` для точного измерения
- Прямой вызов Telegram API функции без обёрток
- Минимизация операций между обнаружением и кликом

#### 4. BookingScheduler (scheduler.py)

**Назначение:** Планирование задач бронирования

**Основные методы:**
- `schedule_daily_booking()` - Ежедневное бронирование
- `schedule_one_time_booking()` - Однократное бронирование
- `calculate_timing()` - Расчет временных параметров
- `get_scheduled_jobs()` - Список запланированных задач

**Использует:** APScheduler для точного планирования

### Config модули

#### 5. Settings (settings.py)

**Назначение:** Загрузка и валидация конфигурации

**Структура конфигурации:**
```yaml
telegram:      # API credentials
bot:           # Bot settings
booking:       # Booking parameters
targets:       # Target shipments (priority-based)
performance:   # Performance thresholds
notifications: # Notification settings
```

**Валидация:** Pydantic для строгой типизации и проверки

**Поддержка environment variables:**
- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_PHONE`
- `BOT_USERNAME`

#### 6. SessionManager (session_manager.py)

**Назначение:** Управление Telegram сессиями

**Основные методы:**
- `get_session_path()` - Путь к файлу сессии
- `session_exists()` - Проверка существования
- `delete_session()` - Удаление сессии
- `backup_session()` - Резервное копирование
- `restore_session()` - Восстановление

**Безопасность:** Сессии хранятся в отдельной директории `sessions/`

### Utils модули

#### 7. Logger (logger.py)

**Назначение:** Продвинутое логирование с использованием Loguru

**Три типа вывода:**
1. **Console** - цветной вывод с миллисекундами
2. **File** - текстовый лог с ротацией
3. **JSON** - структурированный лог для анализа

**Особенности:**
- Точность до миллисекунд
- Автоматическая ротация (10 MB)
- Сжатие старых логов
- Асинхронная запись (enqueue=True)

#### 8. MetricsCollector (metrics.py)

**Назначение:** Сбор и анализ метрик производительности

**Функционал:**
- Запись времени выполнения действий
- Таймеры для замера длительности
- Счетчики событий
- Статистическая обработка (min, max, avg)

**Методы:**
- `record_action()` - Запись действия
- `start_timer()` / `stop_timer()` - Управление таймерами
- `get_statistics()` - Получение статистики
- `print_summary()` - Красивый вывод метрик

#### 9. Notifier (notifier.py)

**Назначение:** Уведомления пользователя

**Типы уведомлений:**
- Startup banner с конфигурацией
- Countdown timer
- Success/failure результаты
- Telegram сообщения (опционально)
- Звуковые сигналы

**Цветовой вывод:** ANSI escape-коды для консоли

## Потоки данных

### Поток 1: Инициализация

```
main.py
  ↓
load_settings() → Settings
  ↓
BookingClient.initialize() → Telegram Auth
  ↓
BotHandler.initialize() → Get last message ID
  ↓
Ready for monitoring
```

### Поток 2: Мониторинг и бронирование

```
monitor_sms() [30ms polling]
  ↓
SMS detected!
  ↓
execute_booking_sequence()
  ├─ send_message("/start")         [Stage 1]
  ├─ get_latest_messages()          [Get menu]
  ├─ button_clicker.ultra_fast_click() [Stage 2]
  ├─ get_latest_messages()          [Get confirm]
  └─ button_clicker.click_confirm()  [Stage 3]
  ↓
notify_booking_result()
```

### Поток 3: Метрики

```
Action execution
  ↓
metrics.record_action()
  ↓
metrics.get_statistics()
  ↓
notifier.notify_booking_result()
```

## Временные характеристики

### Целевые показатели

| Этап | Целевое время | Описание |
|------|--------------|----------|
| SMS → /start | < 50ms | Обнаружение SMS и отправка команды |
| /start → select | < 50ms | Получение меню и выбор перевозки |
| select → confirm | < 30ms | Получение и клик подтверждения |
| **Итого** | **< 150ms** | Полный цикл бронирования |

### Факторы, влияющие на производительность

1. **Сетевые задержки**
   - Пинг до Telegram DC
   - Скорость соединения
   - Выбор datacenter

2. **Системные задержки**
   - CPU загрузка
   - Тип диска (SSD vs HDD)
   - Количество фоновых процессов

3. **Программные задержки**
   - Polling interval (30ms)
   - Sleep между операциями (15ms)
   - Обработка ответов

## Конфигурация производительности

### Polling Interval

```yaml
performance:
  polling_interval_ms: 30  # Баланс между скоростью и нагрузкой
```

**Соображения:**
- Меньше = быстрее обнаружение, но больше запросов
- Больше = меньше нагрузка, но медленнее обнаружение
- Рекомендуется: 30-50ms

### Preparation Time

```yaml
booking:
  preparation_time_seconds: 60  # Начать за 60 сек
  monitoring_start_seconds: 10  # Интенсивный мониторинг за 10 сек
```

**Этапы:**
1. **Ожидание** (до preparation_time)
2. **Подготовка** (60-10 сек до цели)
3. **Мониторинг** (последние 10 сек)
4. **Выполнение** (при обнаружении SMS)

## Обработка ошибок

### Типы ошибок

1. **Сетевые ошибки**
   - Connection timeout
   - Network unreachable
   - **Обработка:** Retry с exponential backoff

2. **Telegram ошибки**
   - FloodWaitError
   - AuthKeyUnregisteredError
   - **Обработка:** Ожидание или реавторизация

3. **Бизнес-логика**
   - Кнопка не найдена
   - Неожиданная структура сообщения
   - **Обработка:** Fallback стратегии

### Retry механизм

```python
for attempt in range(max_retries):
    try:
        return await operation()
    except Exception as e:
        if attempt == max_retries - 1:
            raise
        await asyncio.sleep(0.01 * (2 ** attempt))
```

## Безопасность

### Хранение credentials

- API credentials в `config.yaml` (не в git)
- Сессии в директории `sessions/` (не в git)
- Environment variables как альтернатива

### Ограничения Telegram

- Rate limiting (FloodWait)
- Максимум запросов в секунду
- **Соблюдение:** Адекватные интервалы между запросами

## Масштабирование

### Мультиаккаунт (будущая функция)

```python
clients = [
    BookingClient(api_id1, api_hash1, phone1),
    BookingClient(api_id2, api_hash2, phone2),
]

# Параллельное выполнение
await asyncio.gather(*[
    client.run_booking() for client in clients
])
```

### Distributed mode (будущая функция)

- Redis для координации
- Shared state между экземплярами
- Leader election

## Тестирование

### Unit тесты
- Тестирование отдельных модулей
- Mock Telegram API
- Проверка метрик

### Integration тесты
- Тестовый бот
- Измерение реальной производительности
- End-to-end сценарии

### Performance тесты
- Бенчмарки времени реакции
- Стресс-тестирование
- Профилирование узких мест

## Мониторинг и отладка

### Логирование

**Уровни:**
- DEBUG - детальная информация для отладки
- INFO - основные события
- WARNING - предупреждения
- ERROR - ошибки

**Файлы:**
- `logs/booking_client.log` - текстовый лог
- `logs/booking_client_json.log` - JSON для парсинга

### Метрики

**Собираются:**
- Время каждого действия
- Количество успешных/неудачных попыток
- Статистика за сессию

**Экспорт:**
- JSON format
- Возможность интеграции с Prometheus (будущее)

## Развертывание

### Локальное развертывание

```bash
./setup_client.sh
source venv/bin/activate
python main.py --mode immediate
```

### Production deployment

**Systemd service:**
```ini
[Unit]
Description=Auto Booking Client
After=network.target

[Service]
Type=simple
User=booking
WorkingDirectory=/opt/auto_booking
ExecStart=/opt/auto_booking/venv/bin/python main.py --mode scheduled
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Docker (будущая функция)

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements-client.txt .
RUN pip install -r requirements-client.txt
COPY . .
CMD ["python", "main.py"]
```

## Зависимости

### Основные

- **telethon** - Telegram MTProto API
- **pydantic** - Валидация конфигурации
- **loguru** - Продвинутое логирование
- **APScheduler** - Планирование задач

### Вспомогательные

- **aiohttp** - Async HTTP (для будущих функций)
- **PyYAML** - Парсинг YAML
- **python-dotenv** - Environment variables
- **cryptography** - Криптография для сессий

## Лицензия и использование

**⚠️ Важно:** Автоматизация может нарушать ToS Telegram. Используйте ответственно.

**Рекомендуется:**
- Тестирование собственных ботов
- Исследовательские цели
- Демонстрация концепции

**Не рекомендуется:**
- Спам
- Абузив ботов третьих лиц
- Нарушение правил сервиса
