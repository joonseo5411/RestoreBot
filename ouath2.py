from quart import request

from datetime import datetime
from datetime import timedelta
import requests
import asyncio
import setting
import pytz

async def serverCheck(guildID):
    response = requests.get(
        f'https://discord.com/api/v10/users/@me/guilds',
        headers = {'Authorization': f'Bot {setting.token}'})
    
    if response.status_code == 200:
        guilds = response.json()
        for guild in guilds:
            if guild['id'] == str(guildID):
                return True
        return False
    return False

def serverTime():
    KST= pytz.timezone(setting.timeZone)
    return datetime.now().astimezone(KST)

async def exchange_code(code, redirect_url):
    # Data Posting
    data = {
        'grant_type': 'authorization_code',
        'redirect_uri':  redirect_url,
        'client_id': setting.client_id,
        'client_secret':setting.client_secret,
        'code':code,
    }

    # Posting headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    while True:
        response=requests.post(f'{setting.api_endpoint}/oauth2/token', data=data, headers=headers)

        if response.status_code != 429:
            break
        
        # retry error command
        limitinfo = response.json()
        await asyncio.sleep(limitinfo["retry_after"] + 2)

    return False if "error" in response.json() else response.json()

async def getIp():
    """Getting user's first IP"""
    ip = request.headers.get('X-Forwarded-For')

    if not ip:
        ip = request.remote_addr

    ip = ip.split(",")[0].strip()

    return ip

async def getIpInfo(ipAddress):
    response = requests.get(f'http://ip-api.com/json/{ipAddress}')
    if response.status_code == 200:
        data = response.json()
        isp = data.get('isp')
        city = data.get('city')
        country = data.get('country')
        if isp and city and country:
            return isp, city, country
    return None

async def getAgent():
    return request.user_agent.string

async def isExpired(time):
    ServerTime = serverTime()
    ExpireTime = datetime.strptime(time, "%Y-%m-%d %H:%M")

    return True if (ExpireTime - ServerTime).total_seconds() > 0 else False

async def get_expiretime(time):
    ServerTime = serverTime()
    ExpireTime = datetime.strptime(time, "%Y-%m-%d %H:%M")

    if (ExpireTime - ServerTime).total_seconds() > 0:
        howLong = ExpireTime - ServerTime
        days = howLong.days
        hours = howLong.seconds // 3600
        minutes = howLong.seconds // 60 - hours * 60
        print(minutes)
        return (
            str(round(days)) + "Days" +
            str(round(hours)) + "hours" +
            str(round(minutes)) + "minutes"
        )
    else:
        return False
    
async def make_expireitme(days):
    return (serverTime() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M")

async def add_time(nowDays, addDays):
    ExpireTime = datetime.strptime(nowDays, "%Y-%m-%d %H:%M")
    return (ExpireTime + timedelta(days=addDays)).strftime("%Y-%m-%d %H:%M")

async def getGuild(id):
    response = requests.get(
        f'https://discord.com/apt/v9/guilds/{id}',
        headers={"Authorization": f"Bot {setting.token}"})

    return response.json()

async def getUserProfile2(token):
    response = requests.get(
        "https://discordapp.com/apt/v8/users/@me",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(response.json())
    return False if response.status_code != 200 else response.json()

async def getUserProfile(token):
    response = requests.get(
        "https://discord.com/v10/users/@me",
        headers={"Authorization": token}
    )

    print(response.json())
    return False if response.status_code != 200 else response.json()