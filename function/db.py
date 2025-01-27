import aiosqlite, os
from .logger import logger
from random import choices
from discord import Object
import asyncio
import string
import time

db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'logs', 'database.db'))

class DB:
    def key_generate(number:int = 5, r=4):
        return '-'.join([''.join(choices(string.ascii_letters + string.digits, k=number)) for _ in range(r)])

    @classmethod
    async def create_table(cls):
        async with aiosqlite.connect(db_path) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS restore (
                                    user TEXT,
                                    webhook TEXT,
                                    role_id INTEGER,
                                    guild_id INTEGER,
                                    expire_date INTEGER,
                                    restoreKey TEXT,
                                    PRIMARY KEY(user, role_id, webhook, guild_id, expire_date, restoreKey)
                                    )''')

            await db.execute('''CREATE TABLE IF NOT EXISTS restore_license (
                            registerKEY TEXT,
                            expireDate INTEGER,
                            PRIMARY KEY (registerKEY, expireDate)
                                    )''')
            await db.commit()

    @classmethod
    async def add_user(cls, user_id: int, refresh_token: str, guild_id: int):
        async with aiosqlite.connect(db_path) as db:
            result = await db.execute(
                "SELECT user_id, role_id, webhook FROM restore WHERE guild_id = ?", 
                (guild_id)
            )
            response = await result.fetchone()
            if not response:
                return False

            user = eval(response[0]).append([user_id, refresh_token])
            await db.execute("UPDATE restore SET user = ? WHERE guild_id = ?", (str(user), guild_id))            
            await db.commit()
            return str(response[1]), str(eval(response[2])[1])

    @classmethod
    async def set_role(cls, role_id: int, guild_id: int):
        async with aiosqlite.connect(db_path) as db:
            try:
                await db.execute(
                    "UPDATE restore SET role_id = ? WHERE guild_id = ?",
                    (role_id, guild_id)
                )
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"{guild_id} 서버에서 에러가 발생했어요. ({e})")
                return e

    @classmethod
    async def createLicense(cls, days: int, amount: int):        
        async with aiosqlite.connect(db_path) as db:
            licenses = []
            for _ in range(amount):
                license_key = cls.key_generate()
                await db.execute("INSERT INTO restore_license VALUES (?, ?)",
                                (license_key, int(days*86400)))
                licenses.append(license_key)
            await db.commit()
            return licenses
            
    @classmethod
    async def registerGuild(cls, guildID: int, licenseID: str):
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("SELECT user FROM restore WHERE guild_id = ?", (guildID,)) as cursor:
                guildData = await cursor.fetchone()
                if guildData:
                    return False

            async with db.execute("SELECT * FROM restore_license WHERE registerKEY = ?", (str(licenseID),)) as cursor:
                licenseInfo = await cursor.fetchone()
                logger.info(str(licenseInfo))

            if not licenseInfo:
                return False

            await db.execute(
                "INSERT INTO restore (user, webhook, role_id, guild_id, expire_date, restoreKey) VALUES (?, ?, ?, ?, ?, ?)",
                (str([]), str([False, False]), None, guildID, int(time.time() + int(licenseInfo[1])), cls.key_generate(5, 1))
            )

            await db.execute("DELETE FROM restore_license WHERE registerKEY = ?", (licenseID,))
            await db.commit()

            return True

    @classmethod
    async def getGuildInfo(cls, guildID):
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("SELECT * FROM restore WHERE guild_id = ?", (guildID,)) as cursor:
                data = await cursor.fetchone()
                if not data:
                    return False
                return data

    @classmethod
    async def getGuildRegister(cls):
        async with aiosqlite.connect(db_path) as db:
            guilds = []
            res = await db.execute("SELECT guild_id FROM restore")
            if not res:
                return []
            result = await res.fetchall()
            for x in range(len(result)):
                guildID = result[x][0]
                if guildID != 0:
                    guilds.append(Object(guildID))

            return guilds