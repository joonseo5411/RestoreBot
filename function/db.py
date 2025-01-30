import aiosqlite, os
from .logger import logger
from random import choices
from discord import Object
import asyncio, string, time

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
            async with db.execute("SELECT user, role_id, webhook FROM restore WHERE guild_id = ?", (guild_id, )) as result:
                response = await result.fetchone()
                if not response:
                    return False, False

                usrDB = eval(response[0])
                if not str(user_id) in str(usrDB):
                    usrDB.append([user_id, refresh_token])
                    await db.execute("UPDATE restore SET user = ? WHERE guild_id = ?", (str(usrDB), guild_id))            
                    await db.commit()
                return str(response[1]), str(eval(response[2])[0])

    @classmethod
    async def set_role(cls, role_id: int, guild_id: int):
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("UPDATE restore SET role_id = ? WHERE guild_id = ?", (role_id, guild_id)) as cursor:
                await db.commit()
                return True

    @classmethod
    async def set_webhook(cls, webhook: list, guildID: int):
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("UPDATE restore SET webhook = ? WHERE guild_id = ?", (str(webhook), guildID)) as cursor:
                await db.commit()
                return True

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
            async with db.execute("SELECT * FROM restore_license WHERE registerKEY = ?", (str(licenseID),)) as cursor:
                licenseInfo = await cursor.fetchone()

                if not licenseInfo:
                    return False

                async with db.execute("SELECT expire_date FROM restore WHERE guild_id = ?", (guildID,)) as cursor:
                    guildInfo = await cursor.fetchone()

                if not guildInfo:
                    key = cls.key_generate(5, 1)
                    await db.execute(
                    "INSERT INTO restore (user, webhook, role_id, guild_id, expire_date, restoreKey) VALUES (?, ?, ?, ?, ?, ?)",
                    (str([]), str([False, False]), None, guildID, int(time.time() + int(licenseInfo[1])), key)
                    )
                else:
                    key = True
                    await db.execute("UPDATE restore SET expire_date = ? WHERE guild_id = ?", (int(guildInfo[0]) + int(licenseInfo[1]), guildID))

                await db.execute("DELETE FROM restore_license WHERE registerKEY = ?", (licenseID,))
                await db.commit()
                return key

    @classmethod
    async def getGuildInfo(cls, guildID):
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("SELECT * FROM restore WHERE guild_id = ?", (guildID,)) as cursor:
                data = await cursor.fetchone()
                if not data:
                    return False
                return data
    
    @classmethod
    async def isExpired(cls, guildID):
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("SELECT expire_date FROM restore WHERE guild_id = ?", (guildID,)) as cursor:
                data = await cursor.fetchone()
                if not data:
                    return False
                
                if int(data[0]) > time.time():
                    return True
                
                return False

    @classmethod
    async def getRestoreKey(cls, key: str):
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("SELECT user FROM restore WHERE restoreKey = ?", (str(key),)) as cursor:
                data = await cursor.fetchone()
                if not data:
                    return False
                
                return eval(data[0])

    @classmethod
    async def changeRefreshToken(cls, old_usr, new_usr):
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("UPDATE restore SET user = ? WHERE user = ?", (str(new_usr), str(old_usr),)) as cursor:
                await db.commit()
                return
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
