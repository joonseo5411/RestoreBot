import aiosqlite, os
from logger import logger
import string
import time

db_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'database.db')

class DB:
    def key_generate(number:int = 5):
        return '-'.join([''.join(choices(string.ascii_letters + string.digits, k=5)) for _ in range(4)])

    @classmethod
    async def create_table(cls):
        async with aiosqlite.connect(db_path) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS restore (
                                    refresh_token TEXT,
                                    user_id INTEGER,
                                    role_id INTEGER,
                                    guild_id INTEGER,
                                    PRIMARY KEY(refresh_token, user_id, role_id, guild_id)
                                    )''')

            await db.execute('''CREATE TABLE IF NOT EXISTS restore_license (
                                    status BOOLEAN,
                                    guild_id INTEGER,
                                    license INTEGER,
                                    date INTEGER,
                                    PRIMARY KEY(status, guild_id, license, date)
                                    )''')
            await db.commit()

    @classmethod
    async def add_user(cls, user_id: int, refresh_token: str, guild_id: int):
        async with aiosqlite.connect(db_path) as db:
            try:
                await db.execute(
                    "INSERT INTO restore VALUES (?, ?, ?)", 
                    (user_id, refresh_token, guild_id)
                )
                await db.commit()
                return True
            except Exception as e:
                print(f"Error Exception: {e}")
                return e

    @classmethod
    async def set_role(cls, role_id: int, guild_id: int):
        async with aiosqlite.connect(db_path) as db:
            try:
                await db.execute(
                    "UPDATE restore SET role_id = ? WHERE guild = ?",
                    (role_id, guild_id)
                )
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"{guild_id} 서버에서 에러가 발생했어요. ({e})")
                return e

    @classmethod
    async def create_license(cls, date: int):        
        async with aiosqlite.connect(db_path) as db:
            license_key = cls.key_generate()
            try:
                await db.execute("INSERT INTO restore_license VALUES (?, ?, ?, ?)",
                                (False, 0, license_key, time.time()))
                await db.commit()
                return True, license_key
            except Exception as e:
                return e, None