import time
from datetime import datetime
from typing import Optional


class Timer:
    def __init__(self):
        self.start_time = None
        
    def start(self):
        self.start_time = time.time()
        
    def stop(self) -> float:
        if self.start_time is None:
            return 0.0
        elapsed = (time.time() - self.start_time) * 1000
        return round(elapsed, 3)
    
    def get_elapsed(self) -> float:
        if self.start_time is None:
            return 0.0
        elapsed = (time.time() - self.start_time) * 1000
        return round(elapsed, 3)


def format_shipment_info(shipment: dict) -> str:
    shipment_type = "Прямая перевозка" if shipment['type'] == 'direct' else "Магистральная перевозка"
    status = "❌ Забронировано" if shipment['is_booked'] else "✅ Доступно"
    
    text = f"📦 <b>{shipment_type}</b>\n\n"
    text += f"🏙️ <b>Город:</b> {shipment['city']}\n"
    text += f"📊 <b>Количество:</b> {shipment['quantity']}\n"
    text += f"📌 <b>Статус:</b> {status}\n"
    
    if shipment['is_booked'] and shipment['booked_at']:
        text += f"⏰ <b>Забронировано:</b> {shipment['booked_at']}\n"
    
    return text


def format_test_results(stage1_ms: float, stage2_ms: float, total_ms: float) -> str:
    stage1_sec = stage1_ms / 1000
    stage2_sec = stage2_ms / 1000
    total_sec = total_ms / 1000
    
    text = "⏱️ <b>РЕЗУЛЬТАТЫ ТЕСТА</b>\n\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n"
    text += "📊 <b>Скорость отклика:</b>\n\n"
    text += f"От SMS до /start: <code>{stage1_sec:.3f}</code> сек\n"
    text += f"От /start до выбора: <code>{stage2_sec:.3f}</code> сек\n"
    text += f"Общее время: <code>{total_sec:.3f}</code> сек\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "✅ Перевозка выбрана успешно!"
    
    return text


def format_booking_result(success: bool, message: str, response_time_ms: float) -> str:
    response_time_sec = response_time_ms / 1000
    
    if success:
        text = f"✅ {message}\n\n"
    else:
        text = f"❌ {message}\n\n"
    
    text += f"⏱️ <b>Время обработки:</b> <code>{response_time_sec:.3f}</code> сек"
    
    return text


def format_stats(stats: dict) -> str:
    text = "📊 <b>СТАТИСТИКА БОТА</b>\n\n"
    text += f"👥 Активных пользователей: <b>{stats['users_count']}</b>\n"
    text += f"✅ Успешных бронирований: <b>{stats['bookings_count']}</b>\n"
    text += f"⏱️ Средняя скорость: <code>{stats['avg_response_time']:.3f}</code> мс\n"
    
    return text


def format_user_logs(logs: list) -> str:
    if not logs:
        return "📝 Логи отсутствуют"
    
    text = "📝 <b>ЛОГИ ПОЛЬЗОВАТЕЛЯ</b>\n\n"
    for log in logs[:10]:
        timestamp = log['timestamp']
        action = log['action']
        success = "✅" if log['success'] else "❌"
        response_time = f" ({log['response_time_ms']:.3f} мс)" if log['response_time_ms'] else ""
        
        text += f"{success} <code>{timestamp}</code> - {action}{response_time}\n"
    
    return text
