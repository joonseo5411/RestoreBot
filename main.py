from discord.ext import commands
from datetime import datetime
import discord

from function import setting
from function import DB

from function import logger
import asyncio

guilds = []

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="..", help_command=None, intents=intents)

def error_function(error, i: discord.Interaction):
    if isinstance(error, commands.MissingPermissions):
        logger.warning(f"{i.user.name}({i.user.id}) 님의 권한 부족으로 명령어가 실행 하지 못했어요.")

    if isinstance(error, commands.CommandError):
        logger.warning(f'{i.user.name}({i.user.id}) 님이 명령어를 실행 하였지만, {error}의 에러가 방생 하였습니다.')

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
async def verify(i: discord.Interaction):
    logger.info(f'{i.user.name}({i.user.id}) 님이 {i.guild.name}({i.guild.id})에서 인증 명령어를 실행 하셨습니다.')
    await i.response.send_message("출력 준비 중", ephemeral=True)
    msg = await i.original_response()

    setting = setting()
    verfiy = f'https://discord.com/api/oauth2/authorize?client_id={setting.client_id}&redirect_uri={setting.base_url}%2Fcallback&response_type=code&scope=identify+email+guilds.join&state={i.guild.id}'
    embed = discord.Embed(
        title=f"{i.guild.name}",
        description=f"Please authorize your account [here]({verfiy}) to see other channels.\n다른 채널을 보려면 [여기]({verfiy}) 를 눌러 계정을 인증해주세요."
    )

    button = discord.ui.Button(style=discord.ButtonStyle.link,label="인증하기",disabled=False, emoji="🌐", url=verfiy)
    view = discord.ui.View()
    view.add_item(button)

    await i.channel.send(embed=embed, view=view)
    return await msg.edit(content="출력 완료")

@bot.tree.command(name="역할설정", description="🔰ㅣ인증 완료 후, 받을 역할을 설정 해 주세요.",guilds=guilds)
@discord.app_commands.describe(
    role="🔰ㅣ인증 후, 받으실 역할을 설정 해 주세요."
)
@commands.has_permissions(administrator=True)
@discord.app_commands.guild_only()
async def set_role(i: discord.Interaction, role: discord.Role):
    role_id = role.id

    boolean = await DB.set_role(role_id, i.guild_id)
    if boolean:
        embed = discord.Embed(title="역할 등록 완료",
            description=f"- 적용된 역할: {role.mention}\n" +
                        f"- 적용된 역할ID: {role}",
            timestamp=datetime.now(),
            color=discord.Color.green())
        embed.set_footer(text=f"{bot.user.name}", icon_url=f"{bot.user.avatar}")
        return await i.response.send_message(embed=embed,ephemeral=True)

    embed = discord.Embed(title="역할 등록 실패",
        description="- **사유**\n"+
                    f"- -# {boolean}",
        timestamp=datetime.now(),
        color=discord.Color.red())

    embed.set_footer(text=f"{bot.user.name}", icon_url=f"{bot.user.avatar}")
    return await i.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name='등록', description='📥ㅣ서버를 등록 합니다.')
@discord.app_commands.guild_only()
@commands.has_permissions(administrator=True)
async def register(i: discord.Interaction):
    class registerModal(discord.ui.Modal, title='📥ㅣ등록하기'):
        licenseVar = discord.ui.TextInput(
            label='라이센스 키를 입력 해 주세요.',
            style=discord.TextStyle.short,
            placeholder='1s3w5-1f3df-1cvbs-qwert',
            max_length=23,
            min_length=23
        )

        async def on_submit(self, interaction: discord.Interaction):
            licenseKEY = self.licenseVar
            registers = await DB.registerGuild(i.guild_id, licenseKEY)
            if not registers:
                embed = discord.Embed(title='Not found license key',
                    description='- please check license key again and use command later',
                    color=discord.Color.red())
                return await interaction.response.send_message(embed=embed, ephemeral=True)
    return await i.response.send_modal(registerModal())

@bot.command(name="생성")
async def createLicense(ctx, days: int, amount:int = 1):
    if not bot.is_owner:
        return

    result = await DB.createLicense(days, amount)
    return await ctx.send(("\n".join(result)).join(days))

@verify.error
async def verify_error(error, i: discord.Interaction):
    error_function(error, i)

@set_role.error
async def setRoleError(error, i: discord.Interaction):
    error_function(error, i)

async def botRun():
    await bot.start(setting().token)

asyncio.run(botRun())