from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict


def get_main_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="Список прямых перевозок", callback_data="direct_shipments"),
            InlineKeyboardButton(text="Список магистральных перевозок", callback_data="main_shipments")
        ],
        [
            InlineKeyboardButton(text="Мои перевозки", callback_data="my_shipments"),
            InlineKeyboardButton(text="Настройки", callback_data="settings")
        ],
        [
            InlineKeyboardButton(text="🧪 Тест", callback_data="test_mode")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_shipments_keyboard(shipments: List[Dict], shipment_type: str) -> InlineKeyboardMarkup:
    keyboard = []
    for shipment in shipments:
        btn_text = f"{shipment['city']}_{shipment['quantity']}"
        if shipment['is_booked']:
            btn_text += " ❌"
        keyboard.append([
            InlineKeyboardButton(
                text=btn_text, 
                callback_data=f"shipment:{shipment['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_shipment_detail_keyboard(shipment_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm:{shipment_id}")],
        [InlineKeyboardButton(text="◀️ Возврат в меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_test_result_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🔄 Повторить тест", callback_data="test_mode")],
        [InlineKeyboardButton(text="◀️ В главное меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
