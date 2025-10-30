import asyncio
import logging
import sys
import os
from datetime import datetime, time as dt_time
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import time

import config
import database
import keyboards
import utils

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

user_timers = {}
test_sessions = {}


class TestState(StatesGroup):
    waiting_for_start = State()
    waiting_for_selection = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    await database.add_user(user_id, username, first_name)
    
    current_state = await state.get_state()
    
    if current_state == TestState.waiting_for_start.state and user_id in test_sessions:
        test_data = test_sessions[user_id]
        test_data['start_command_time'] = time.time()
        stage1_ms = (test_data['start_command_time'] - test_data['test_start_time']) * 1000
        test_data['stage1_ms'] = stage1_ms
        
        await database.update_test_session_start(user_id)
        await database.add_log(user_id, 'test_start_command', stage1_ms, True, True, 'start_pressed')
        
        await state.set_state(TestState.waiting_for_selection)
        
        test_shipments = await database.get_shipments('test', is_test=True)
        if not test_shipments:
            for shipment in config.TEST_SHIPMENTS:
                await database.add_shipment('test', shipment['city'], shipment['quantity'], is_test=True)
            test_shipments = await database.get_shipments('test', is_test=True)
        
        await message.answer(
            "🧪 <b>ТЕСТОВЫЙ РЕЖИМ</b>\n\nВыберите перевозку:",
            reply_markup=keyboards.get_shipments_keyboard(test_shipments, 'test'),
            parse_mode='HTML'
        )
        return
    
    await state.clear()
    
    welcome_text = "Пришлем сообщение как только будут назначены перевозки"
    
    if os.path.exists(config.WELCOME_IMAGE_PATH):
        photo = FSInputFile(config.WELCOME_IMAGE_PATH)
        await message.answer_photo(
            photo=photo,
            caption=welcome_text,
            reply_markup=keyboards.get_main_menu()
        )
    else:
        await message.answer(
            welcome_text,
            reply_markup=keyboards.get_main_menu()
        )
    
    await database.add_log(user_id, 'start_command')


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    welcome_text = "Пришлем сообщение как только будут назначены перевозки"
    
    if os.path.exists(config.WELCOME_IMAGE_PATH):
        await callback.message.delete()
        photo = FSInputFile(config.WELCOME_IMAGE_PATH)
        await callback.message.answer_photo(
            photo=photo,
            caption=welcome_text,
            reply_markup=keyboards.get_main_menu()
        )
    else:
        await callback.message.edit_text(
            welcome_text,
            reply_markup=keyboards.get_main_menu()
        )
    
    await callback.answer()


@router.callback_query(F.data == "direct_shipments")
async def show_direct_shipments(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    shipments = await database.get_shipments('direct')
    
    await callback.message.edit_text(
        "📦 <b>Список прямых перевозок:</b>",
        reply_markup=keyboards.get_shipments_keyboard(shipments, 'direct'),
        parse_mode='HTML'
    )
    await callback.answer()
    await database.add_log(callback.from_user.id, 'view_direct_shipments')


@router.callback_query(F.data == "main_shipments")
async def show_main_shipments(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    shipments = await database.get_shipments('main')
    
    await callback.message.edit_text(
        "📦 <b>Список магистральных перевозок:</b>",
        reply_markup=keyboards.get_shipments_keyboard(shipments, 'main'),
        parse_mode='HTML'
    )
    await callback.answer()
    await database.add_log(callback.from_user.id, 'view_main_shipments')


@router.callback_query(F.data == "my_shipments")
async def show_my_shipments(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    bookings = await database.get_user_bookings(user_id)
    
    if not bookings:
        text = "У вас пока нет забронированных перевозок"
    else:
        text = "📋 <b>Ваши забронированные перевозки:</b>\n\n"
        for booking in bookings:
            shipment_type = "Прямая" if booking['type'] == 'direct' else "Магистральная"
            text += f"• {shipment_type}: {booking['city']} (кол-во: {booking['quantity']})\n"
            text += f"  Забронировано: {booking['booked_at']}\n\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboards.get_back_to_menu_keyboard(),
        parse_mode='HTML'
    )
    await callback.answer()
    await database.add_log(user_id, 'view_my_shipments')


@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    user = await database.get_user(user_id)
    
    text = "⚙️ <b>Настройки</b>\n\n"
    text += f"👤 User ID: <code>{user_id}</code>\n"
    text += f"👤 Username: @{user['username'] if user['username'] else 'Не указан'}\n"
    text += f"📅 Дата регистрации: {user['registration_date']}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboards.get_back_to_menu_keyboard(),
        parse_mode='HTML'
    )
    await callback.answer()
    await database.add_log(user_id, 'view_settings')


@router.callback_query(F.data == "test_mode")
async def start_test_mode(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    session_id = await database.create_test_session(user_id)
    
    test_sessions[user_id] = {
        'session_id': session_id,
        'test_start_time': time.time()
    }
    
    await state.set_state(TestState.waiting_for_start)
    
    await callback.message.edit_text(
        "🧪 Тест запущен!\n\nСейчас будет отправлена имитация SMS...",
        reply_markup=None
    )
    await callback.answer()
    
    await asyncio.sleep(1)
    
    await callback.message.answer(
        "Появились новые перевозки.\n\nНажмите /start для вызова меню"
    )
    
    await database.add_log(user_id, 'test_sms_sent', is_test_mode=True, test_stage='sms_sent')


@router.callback_query(F.data.startswith("shipment:"))
async def show_shipment_detail(callback: CallbackQuery, state: FSMContext):
    shipment_id = int(callback.data.split(':')[1])
    user_id = callback.from_user.id
    
    timer = utils.Timer()
    timer.start()
    user_timers[f"{user_id}:{shipment_id}"] = timer
    
    shipment = await database.get_shipment(shipment_id)
    
    if not shipment:
        await callback.answer("Перевозка не найдена", show_alert=True)
        return
    
    current_state = await state.get_state()
    
    if current_state == TestState.waiting_for_selection.state and user_id in test_sessions:
        test_data = test_sessions[user_id]
        test_data['selection_time'] = time.time()
        stage2_ms = (test_data['selection_time'] - test_data['start_command_time']) * 1000
        test_data['stage2_ms'] = stage2_ms
        total_ms = test_data['stage1_ms'] + stage2_ms
        test_data['total_ms'] = total_ms
        
        await database.complete_test_session(user_id, test_data['stage1_ms'], stage2_ms, total_ms)
        await database.add_log(user_id, 'test_shipment_selected', stage2_ms, True, True, 'shipment_selected')
        
        result_text = utils.format_test_results(test_data['stage1_ms'], stage2_ms, total_ms)
        
        await callback.message.edit_text(
            result_text,
            reply_markup=keyboards.get_test_result_keyboard(),
            parse_mode='HTML'
        )
        
        await state.clear()
        if user_id in test_sessions:
            del test_sessions[user_id]
        
        await callback.answer()
        return
    
    info_text = utils.format_shipment_info(shipment)
    
    if shipment['is_booked']:
        await callback.message.edit_text(
            info_text + "\n\n❌ Эта перевозка уже забронирована",
            reply_markup=keyboards.get_back_to_menu_keyboard(),
            parse_mode='HTML'
        )
    else:
        await callback.message.edit_text(
            info_text,
            reply_markup=keyboards.get_shipment_detail_keyboard(shipment_id),
            parse_mode='HTML'
        )
    
    await callback.answer()
    await database.add_log(user_id, f'view_shipment_{shipment_id}')


@router.callback_query(F.data.startswith("confirm:"))
async def confirm_booking(callback: CallbackQuery):
    shipment_id = int(callback.data.split(':')[1])
    user_id = callback.from_user.id
    
    timer_key = f"{user_id}:{shipment_id}"
    timer = user_timers.get(timer_key)
    
    if timer:
        response_time_ms = timer.stop()
        del user_timers[timer_key]
    else:
        response_time_ms = 0.0
    
    success, message = await database.book_shipment(shipment_id, user_id)
    
    result_text = utils.format_booking_result(success, message, response_time_ms)
    
    await callback.message.edit_text(
        result_text,
        reply_markup=keyboards.get_back_to_menu_keyboard(),
        parse_mode='HTML'
    )
    
    await callback.answer()
    await database.add_log(user_id, f'confirm_booking_{shipment_id}', response_time_ms, success)


@router.message(Command('admin_reset'))
async def admin_reset(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("❌ У вас нет прав администратора")
        return
    
    await database.reset_bookings()
    await message.answer("✅ Все бронирования сброшены")


@router.message(Command('admin_add_shipment'))
async def admin_add_shipment(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("❌ У вас нет прав администратора")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 4:
            await message.answer("❌ Использование: /admin_add_shipment [тип] [город] [количество]")
            return
        
        shipment_type = parts[1]
        city = parts[2]
        quantity = int(parts[3])
        
        if shipment_type not in ['direct', 'main']:
            await message.answer("❌ Тип должен быть 'direct' или 'main'")
            return
        
        shipment_id = await database.add_shipment(shipment_type, city, quantity)
        await message.answer(f"✅ Перевозка добавлена с ID: {shipment_id}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.message(Command('admin_stats'))
async def admin_stats(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("❌ У вас нет прав администратора")
        return
    
    stats = await database.get_stats()
    text = utils.format_stats(stats)
    await message.answer(text, parse_mode='HTML')


@router.message(Command('admin_logs'))
async def admin_logs(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("❌ У вас нет прав администратора")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Использование: /admin_logs [user_id]")
            return
        
        user_id = int(parts[1])
        logs = await database.get_user_logs(user_id)
        text = utils.format_user_logs(logs)
        await message.answer(text, parse_mode='HTML')
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.message(Command('admin_test_stats'))
async def admin_test_stats(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("❌ У вас нет прав администратора")
        return
    
    sessions = await database.get_test_sessions()
    
    if not sessions:
        await message.answer("📊 Тестовых сессий пока нет")
        return
    
    text = "📊 <b>СТАТИСТИКА ТЕСТОВ</b>\n\n"
    total_sessions = len(sessions)
    avg_total = sum(s['total_time_ms'] for s in sessions if s['total_time_ms']) / total_sessions if total_sessions > 0 else 0
    
    text += f"Всего тестов: <b>{total_sessions}</b>\n"
    text += f"Среднее время: <code>{avg_total:.3f}</code> мс\n\n"
    text += "Последние 5 тестов:\n"
    
    for session in sessions[:5]:
        if session['total_time_ms']:
            text += f"• User {session['user_id']}: <code>{session['total_time_ms']:.3f}</code> мс\n"
    
    await message.answer(text, parse_mode='HTML')


@router.message(Command('admin_trigger_sms'))
async def admin_trigger_sms(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("❌ У вас нет прав администратора")
        return
    
    await send_booking_notification()
    await message.answer("✅ SMS отправлены всем пользователям")


@router.message(Command('open_booking'))
async def open_booking_command(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("❌ У вас нет прав администратора")
        return
    
    await send_booking_notification()
    await message.answer("✅ Бронирование открыто, уведомления отправлены")


async def send_booking_notification():
    async with database.aiosqlite.connect(database.DATABASE_PATH) as db:
        async with db.execute('SELECT user_id FROM users') as cursor:
            users = await cursor.fetchall()
    
    notification_text = "Появились новые перевозки.\n\nНажмите /start для вызова меню"
    
    for user in users:
        try:
            await bot.send_message(user[0], notification_text)
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"Failed to send notification to user {user[0]}: {e}")


async def scheduled_booking_open():
    logger.info("Scheduled booking opening triggered")
    await send_booking_notification()


async def main():
    await database.init_db()
    await database.initialize_default_shipments()
    
    scheduler = AsyncIOScheduler()
    
    booking_time_parts = config.BOOKING_TIME.split(':')
    hour = int(booking_time_parts[0])
    minute = int(booking_time_parts[1])
    
    scheduler.add_job(
        scheduled_booking_open,
        'cron',
        hour=hour,
        minute=minute
    )
    
    scheduler.start()
    
    dp.include_router(router)
    
    logger.info("Bot started")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
