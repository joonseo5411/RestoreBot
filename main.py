from discord.ext import commands
import discord


from datetime import datetime

from function import setting
from function import DB
from function import logger
from button import settingBtn

import asyncio

guilds = []

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="..", help_command=None, intents=intents)

def error_function(error, i: discord.Interaction):
    if isinstance(error, commands.MissingPermissions):
        logger.warning(f"{i.user.name}({i.user.id}) 님의 권한 부족으로 명령어가 실행 하지 못했어요.")

    if isinstance(error, commands.CommandError):
        logger.warning(f'{i.user.name}({i.user.id}) 님이 명령어를 실행 하였지만, {error}의 에러가 방생 하였습니다.')

def isExpired(func):
    async def wrapper(*args):
        interaction = args[0] 
        result = await DB.isExpired(interaction.guild_id)
        if not result:
            embed = discord.Embed(title="⚠️ㅣ라이센스 만료", description="- `/설정`을(를) 통해 라이센스를 연장 하시거나 등록을 하여 주세요.", color=discord.Color.red())
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        return await func(*args)
    return wrapper

@bot.event
async def on_ready():
    await DB.create_table()
    logger.info(f"DB 테이블 생성을 완료 하였습니다. 테이블 이름은 restore 입니다.")
    global guilds
    guilds = await DB.getGuildRegister()
    logger.info("Successful getting verify guild id")
    await bot.wait_until_ready()

    trees = await bot.tree.sync()
    logger.info(f"{bot.user.name} 이(가) 켜졌습니다. {len(trees)} 개의 명령어가 활성화 되었습니다.")
    
@bot.tree.command(name="인증", description="✅ㅣ인증 메시지를 보냅니다.")
@commands.has_permissions(administrator = True)
@discord.app_commands.guild_only()
@isExpired
async def verify(i: discord.Interaction):
    logger.info(f'{i.user.name}({i.user.id}) 님이 {i.guild.name}({i.guild.id})에서 인증 명령어를 실행 하셨습니다.')
    await i.response.send_message("출력 준비 중", ephemeral=True)
    msg = await i.original_response()

    setVar = setting()
    url = f'https://discord.com/api/oauth2/authorize?client_id={setVar.client_id}&redirect_uri={setVar.base_url}%2Fcallback&response_type=code&scope=identify+email+guilds.join&state={i.guild.id}'
    embed = discord.Embed(
        title=f"{i.guild.name}",
        description=f"다른 채널을 보려면 [여기]({url}) 를 눌러 계정을 인증해주세요.\n-# Please authorize your account [here]({url}) to see other channels."
    )

    verifyBtn = discord.ui.Button(label="인증하기", style=discord.ButtonStyle.link, emoji="🌐", url=url)
    view = discord.ui.View(timeout=None)
    view.add_item(verifyBtn)

    await i.channel.send(embed=embed, view=view)
    embed = discord.Embed(title="출력 완료", description="- 인증 임베드를 성공적으로 출력 했습니다.", color=discord.Color.green())
    return await msg.edit(content=None, embed=embed)

@bot.tree.command(name="설정", description="⚙️ᅵ서버 정보를 수정 합니다.")
@commands.has_permissions(administrator = True)
@discord.app_commands.guild_only()
async def restoreSetting(i: discord.Interaction):
    return await settingBtn(i).btn(None)

@bot.command(name="생성")
async def createLicense(ctx, days: int, amount:int = 1):
    if not ctx.author.id in setting().admin_id:
        return

    result = await DB.createLicense(days, amount)
    lic = []
    for res in result: lic.append(f"{res} {days}일")
    logger.info(f"\n".join(lic))
    return await ctx.send((f" \n".join(lic)))

@restoreSetting.error
async def set_error(error, i: discord.Interaction):
    error_function(error, i)

async def botRun():
    await bot.start(setting().token)

asyncio.run(botRun())