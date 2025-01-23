import aiosqlite, os
from logger import logger
from random import choices
from discord import Object
import string
import time

db_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'database.db')

class DB:
    def key_generate(number:int = 5):
        return '-'.join([''.join(choices(string.ascii_letters + string.digits, k=number)) for _ in range(4)])

    @classmethod
    async def create_table(cls):
        async with aiosqlite.connect(db_path) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS restore (
                                    refresh_token TEXT,
                                    user_id INTEGER,
                                    role_id INTEGER,
                                    webhook TEXT,
                                    webhook_ip TEXT,
                                    guild_id INTEGER,
                                    PRIMARY KEY(refresh_token, user_id, role_id, webhook, webhook_ip, guild_id)
                                    )''')

            await db.execute('''CREATE TABLE IF NOT EXISTS restore_license (
                                    status BOOLEAN,
                                    guild_id INTEGER,
                                    license TEXT,
                                    date INTEGER,
                                    PRIMARY KEY(status, guild_id, license, date)
                                    )''')
            await db.commit()

    @classmethod
    async def add_user(cls, user_id: int, refresh_token: str, guild_id: int):
        async with aiosqlite.connect(db_path) as db:
            try:
                await db.execute(
                    "INSERT INTO restore VALUES refresh_token, user_id, guild_id (?, ?, ?)", 
                    (user_id, refresh_token, guild_id)
                )
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"Error Exception: {e}")
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
    async def create_license(cls, days: int):        
        async with aiosqlite.connect(db_path) as db:
            license_key = cls.key_generate()
            try:
                await db.execute("INSERT INTO restore_license VALUES (?, ?, ?, ?)",
                                (False, 0, license_key, int(time.time() + (days*86400))))
                await db.commit()
                return True, license_key
            except Exception as e:
                return e, None
            
    @classmethod
    async def registerGuild(cls, guildID: int, licenseID: str):
        async with aiosqlite.connect(db_path) as db:
            db.execute("INSERT")

    @classmethod
    async def getGuildRegister(cls):
        async with aiosqlite.connect(db_path) as db:
            guilds = []
            res = await db.execute("SELECT guild_id FROM restore_license")
            if not res:
                return False
            result = res.fetchall()
            for x in range(len(result)):
                guildID = result[x][0]
                if guildID != 0:
                    guilds.append(Object(guildID))

            return guilds