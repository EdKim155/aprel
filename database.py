import aiosqlite
import asyncio
from datetime import datetime
from typing import Optional, List, Dict
import config

DATABASE_PATH = 'bot.db'


async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS shipments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                city TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                is_booked INTEGER DEFAULT 0,
                booked_by INTEGER,
                booked_at TIMESTAMP,
                is_test INTEGER DEFAULT 0,
                FOREIGN KEY (booked_by) REFERENCES users (user_id)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                response_time_ms REAL,
                success INTEGER,
                is_test_mode INTEGER DEFAULT 0,
                test_stage TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS test_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                test_start_time TIMESTAMP,
                start_command_time TIMESTAMP,
                selection_time TIMESTAMP,
                total_time_ms REAL,
                stage1_time_ms REAL,
                stage2_time_ms REAL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        await db.commit()


async def add_user(user_id: int, username: Optional[str], first_name: Optional[str]):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            'INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
            (user_id, username, first_name)
        )
        await db.commit()


async def get_user(user_id: int) -> Optional[Dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def add_shipment(shipment_type: str, city: str, quantity: int, is_test: bool = False) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            'INSERT INTO shipments (type, city, quantity, is_test) VALUES (?, ?, ?, ?)',
            (shipment_type, city, quantity, 1 if is_test else 0)
        )
        await db.commit()
        return cursor.lastrowid


async def get_shipments(shipment_type: str, is_test: bool = False) -> List[Dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            'SELECT * FROM shipments WHERE type = ? AND is_test = ? ORDER BY id',
            (shipment_type, 1 if is_test else 0)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def get_shipment(shipment_id: int) -> Optional[Dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM shipments WHERE id = ?', (shipment_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def book_shipment(shipment_id: int, user_id: int) -> tuple[bool, str]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute('SELECT is_booked, booked_by FROM shipments WHERE id = ?', (shipment_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return False, "Перевозка не найдена"
            
            is_booked, booked_by = row
            if is_booked:
                return False, "К сожалению, перевозка уже забронирована"
        
        await db.execute(
            'UPDATE shipments SET is_booked = 1, booked_by = ?, booked_at = ? WHERE id = ? AND is_booked = 0',
            (user_id, datetime.now().isoformat(), shipment_id)
        )
        await db.commit()
        
        async with db.execute('SELECT changes()') as cursor:
            changes = await cursor.fetchone()
            if changes[0] > 0:
                return True, "Перевозка успешно забронирована!"
            else:
                return False, "К сожалению, перевозка уже забронирована"


async def get_user_bookings(user_id: int) -> List[Dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            'SELECT * FROM shipments WHERE booked_by = ? ORDER BY booked_at DESC',
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def add_log(user_id: int, action: str, response_time_ms: Optional[float] = None, 
                  success: bool = True, is_test_mode: bool = False, test_stage: Optional[str] = None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            '''INSERT INTO logs (user_id, action, response_time_ms, success, is_test_mode, test_stage) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, action, response_time_ms, 1 if success else 0, 1 if is_test_mode else 0, test_stage)
        )
        await db.commit()


async def create_test_session(user_id: int) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            'INSERT INTO test_sessions (user_id, test_start_time) VALUES (?, ?)',
            (user_id, datetime.now().isoformat())
        )
        await db.commit()
        return cursor.lastrowid


async def update_test_session_start(user_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            '''UPDATE test_sessions 
               SET start_command_time = ? 
               WHERE user_id = ? AND id = (
                   SELECT id FROM test_sessions WHERE user_id = ? ORDER BY id DESC LIMIT 1
               )''',
            (datetime.now().isoformat(), user_id, user_id)
        )
        await db.commit()


async def complete_test_session(user_id: int, stage1_ms: float, stage2_ms: float, total_ms: float):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            '''UPDATE test_sessions 
               SET selection_time = ?, stage1_time_ms = ?, stage2_time_ms = ?, total_time_ms = ?
               WHERE user_id = ? AND id = (
                   SELECT id FROM test_sessions WHERE user_id = ? ORDER BY id DESC LIMIT 1
               )''',
            (datetime.now().isoformat(), stage1_ms, stage2_ms, total_ms, user_id, user_id)
        )
        await db.commit()


async def get_test_sessions(user_id: Optional[int] = None) -> List[Dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        if user_id:
            async with db.execute(
                'SELECT * FROM test_sessions WHERE user_id = ? ORDER BY id DESC',
                (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
        else:
            async with db.execute('SELECT * FROM test_sessions ORDER BY id DESC') as cursor:
                rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def reset_bookings():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('UPDATE shipments SET is_booked = 0, booked_by = NULL, booked_at = NULL')
        await db.commit()


async def get_stats() -> Dict:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        async with db.execute('SELECT COUNT(*) as count FROM users') as cursor:
            users_count = (await cursor.fetchone())[0]
        
        async with db.execute('SELECT COUNT(*) as count FROM shipments WHERE is_booked = 1') as cursor:
            bookings_count = (await cursor.fetchone())[0]
        
        async with db.execute(
            'SELECT AVG(response_time_ms) as avg_time FROM logs WHERE response_time_ms IS NOT NULL'
        ) as cursor:
            avg_time = (await cursor.fetchone())[0] or 0
        
        return {
            'users_count': users_count,
            'bookings_count': bookings_count,
            'avg_response_time': avg_time
        }


async def get_user_logs(user_id: int, limit: int = 50) -> List[Dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            'SELECT * FROM logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?',
            (user_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def initialize_default_shipments():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute('SELECT COUNT(*) as count FROM shipments WHERE is_test = 0') as cursor:
            count = (await cursor.fetchone())[0]
        
        if count == 0:
            for shipment in config.DEFAULT_SHIPMENTS['direct']:
                await add_shipment('direct', shipment['city'], shipment['quantity'])
            
            for shipment in config.DEFAULT_SHIPMENTS['main']:
                await add_shipment('main', shipment['city'], shipment['quantity'])
