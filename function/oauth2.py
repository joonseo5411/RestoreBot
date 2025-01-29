from quart import request

from datetime import datetime
from datetime import timedelta
from .setting import setting
from .logger import logger
import requests
import asyncio
import aiohttp
import pytz

async def giveRoleToMember(guildID, memberID, roleID):
    headers ={
        'Authorization': f'Bot {setting().token}',
        'Content-Type': 'application/json'
    }
    async with aiohttp.ClientSession() as session:
        async with session.put(f'{setting().api_endpoint}/guilds/{guildID}/members/{memberID}/roles/{roleID}', headers=headers) as response:
            if response.status == 204:
                return True
            return False

async def serverCheck(guildID):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://discord.com/api/v10/users/@me/guilds', headers = {'Authorization': f'Bot {setting().token}'}) as response:
            if response.status != 200:
                return False
                
            guilds = await response.json()
            for guild in guilds:
                if guild['id'] == str(guildID):
                    return True
            return False

def serverTime():
    KST= pytz.timezone(setting().timeZone)
    return datetime.now().astimezone(KST)

async def exchange_code(code, redirect_url):
    # Data Posting
    data = {
        'grant_type': 'authorization_code',
        'redirect_uri':  redirect_url,
        'client_id': setting().client_id,
        'client_secret':setting().client_secret,
        'code':code,
    }

    # Posting headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.post(f'{setting().api_endpoint}/oauth2/token', data=data, headers=headers) as response:
                data = await response.json()
                if response.status != 429:
                    break
        
                # retry error command
                await asyncio.sleep(limitinfo["retry_after"] + 2)

        return False if "error" in data else data

async def getIp(request):
    """Getting user's first IP"""
    ip = request.headers.get('X-Forwarded-For')

    if not ip:
        ip = request.remote_addr

    ip = ip.split(",")[0].strip()

    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://ip-api.com/json/{ip}') as response:
            if response.status == 200:
                data = await response.json()
                isp = data.get('isp')
                city = data.get('city')
                country = data.get('country')
                if isp and city and country:
                    return ip, isp, city, country
            return ip

async def getAgent():
    return request.user_agent.string

async def getGuild(id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://discord.com/apt/v9/guilds/{id}', headers={"Authorization": f"Bot {setting().token}"}) as response:
            return await response.json()

async def getUserProfile2(token):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://discordapp.com/apt/v8/users/@me", headers={"Authorization": f"Bearer {token}"}) as response:
            return False if response.status != 200 else await response.json()

async def getUserProfile(token):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://discord.com/api/v10/users/@me", headers={"Authorization": "Bearer " + token}) as response:
            return False if response.status != 200 else await response.json()
