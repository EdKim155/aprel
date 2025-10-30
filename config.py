import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]
BOOKING_TIME = os.getenv('BOOKING_TIME', '11:30')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot.db')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
TEST_MODE_ENABLED = os.getenv('TEST_MODE_ENABLED', 'true').lower() == 'true'
MAX_USERS_PER_SHIPMENT = int(os.getenv('MAX_USERS_PER_SHIPMENT', '1'))

WELCOME_IMAGE_PATH = '5445047061721511293.jpg'

TEST_SHIPMENTS = [
    {'city': 'Тест_Москва', 'quantity': 2},
    {'city': 'Тест_СПБ', 'quantity': 3},
    {'city': 'Тест_Казань', 'quantity': 1}
]

DEFAULT_SHIPMENTS = {
    'direct': [
        {'city': 'Челябинск', 'quantity': 3},
        {'city': 'Екатеринбург', 'quantity': 4},
        {'city': 'Новосибирск', 'quantity': 2},
        {'city': 'Омск', 'quantity': 5},
    ],
    'main': [
        {'city': 'Москва', 'quantity': 10},
        {'city': 'Санкт-Петербург', 'quantity': 8},
        {'city': 'Казань', 'quantity': 6},
        {'city': 'Краснодар', 'quantity': 4},
    ]
}
