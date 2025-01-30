from quart import request

from datetime import datetime
from datetime import timedelta
from .setting import setting
from .logger import logger
import asyncio
import aiohttp
import pytz

settingVar = setting()

async def giveRoleToMember(session, guildID, memberID, roleID):    
    async with session.put(f'{settingVar.api_endpoint}/guilds/{guildID}/members/{memberID}/roles/{roleID}', headers ={
        'Authorization': f'Bot {settingVar.token}',
        'Content-Type': 'application/json'
    }) as response:
        if response.status == 204:
            return True
        return False

async def serverCheck(session, guildID):
    async with session.get(f'https://discord.com/api/v10/users/@me/guilds', headers={'Authorization': f'Bot {settingVar.token}'}) as response:
        if response.status != 200:
            return False
        
        guilds = await response.json()
        return next((guild for guild in guilds if guild['id'] == str(guildID)), False)

def serverTime():
    return datetime.now().astimezone(pytz.timezone(settingVar.timeZone))

async def exchange_code(session, code, redirect_url):
    """access user"""
    while True:
        async with session.post(f'{settingVar.api_endpoint}/oauth2/token',
        data = {
        'grant_type': 'authorization_code', 'redirect_uri':  redirect_url,'code':code,
        'client_id': settingVar.client_id, 'client_secret':settingVar.client_secret,
        },
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}) as response:
            data = await response.json()
            if response.status != 429:
                return False if "error" in data else data
            await asyncio.sleep(data["retry_after"] + 2)

async def refreshToken(session, refresh_token):
    while True:
        async with session.post(f"{settingVar.api_endpoint}/oauth2/token",
        data = {
            'client_id': settingVar.client_id, 'client_secret': settingVar.client_secret,
            'grant_type': 'refresh_token', 'refresh_token': refresh_token
        },
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }) as response:
            data = await response.json()
            if response.status != 429:
                return False if "error" in data else data

        await asyncio.sleep(data["retry_after"] + 2)

async def addUser(session, access_token, guild_id, user_id):
    while True:
        jsonData = {"access_token": access_token}
        header = {"Authorization": "Bot " + settingVar.token}
        async with session.put(f"{settingVar.api_endpoint}/guilds/{guild_id}/members/{user_id}", json=jsonData, headers=header) as response:
            data = await response.json()
            if response.status != 429:
                return True if (response.status == 201 or response.status == 204) else False

            await asyncio.sleep(data["retry_after"] + 2)

async def getIp(session, request):
    """Getting user's first IP"""
    ip = (request.headers.get('X-Forwarded-For') or request.remote_addr).split(",")[0].strip()
    agent = request.user_agent.string

    async with session.get(f'http://ip-api.com/json/{ip}') as response:
        if response.status == 200:
            data = await response.json()
            return ip, data.get('isp'), data.get('city'), data.get('country'), agent
    return ip, None, None, None, agent


async def getGuild(session, id):
    async with session.get(f'https://discord.com/apt/v9/guilds/{id}', headers={"Authorization": f"Bot {settingVar.token}"}) as response:
        return await response.json()

async def getRole(session, guildID, id):
    async with session.get(f'https://discord.com/api/v9/guilds/{guildID}/roles', headers={"Authorization": f"Bot {settingVar.token}"}) as response:
        roles = await response.json()
        return next((role for role in roles if role['id'] == id), False)

async def getUserProfile2(session, token):
    async with session.get("https://discordapp.com/apt/v8/users/@me", headers={"Authorization": f"Bearer {token}"}) as response:
        return False if response.status != 200 else await response.json()

async def getUserProfile(session, token):
    async with session.get("https://discord.com/api/v10/users/@me", headers={"Authorization": "Bearer " + token}) as response:
        return False if response.status != 200 else await response.json()
