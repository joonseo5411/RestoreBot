from discord.ext import commands
import discord


from datetime import datetime

from function import setting
from function import DB
from function import isExpired
from function import logger
from function import settingBtn

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
    url = f'https://discord.com/api/oauth2/authorize?client_id={setting.client_id}&redirect_uri={setting.base_url}%2Fcallback&response_type=code&scope=identify+email+guilds.join&state={i.guild.id}'
    embed = discord.Embed(
        title=f"{i.guild.name}",
        description=f"Please authorize your account [here]({url}) to see other channels.\n다른 채널을 보려면 [여기]({url}) 를 눌러 계정을 인증해주세요."
    )

    class verify(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
        
        @discord.ui.button(label="인증하기", style=discord.ButtonStyle.link, emoji="🌐", url=url)
        async def verifyBtn(self, i: discord.Interaction, btn: discord.ui.Button):
            pass

    await i.channel.send(embed=embed, view=verify())
    embed = discord.Embed(title="출력 완료")
    return await msg.edit(content="출력 완료")

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
            registers = await DB.registerGuild(int(i.guild_id), str(self.licenseVar))
            if not registers:
                embed = discord.Embed(title='라이센스 등록 실패',
                    description='- 시도하신 라이센스를 확인 하시고 다시 이용 해 주시길 바랍니다.',
                    color=discord.Color.red())
            else:
                embed = discord.Embed(
                    title="라이센스 등록 성공",
                    description="- `/설정`을 통해 설정을 마무리 해 주세요.\n- `/인증`명령어를 통해 인증 임베드를 출력 가능합니다.",
                    color=discord.Color.green()
                )
            embed.set_footer(text=f"{bot.user.name}", icon_url=f"{bot.user.avatar}")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
    return await i.response.send_modal(registerModal())

@bot.tree.command(name="설정", description="⚙️ᅵ서버 정보를 수정")
@discord.app_commands.guild_only()
@commands.has_permissions(administrator=True)
async def restoreSetting(i: discord.Interaction):
    await settingBtn(i).btn()

@bot.command(name="생성")
async def createLicense(ctx, days: int, amount:int = 1):
    if not ctx.author.id in setting().admin_id:
        return

    result = await DB.createLicense(days, amount)
    lic = []
    for res in result: lic.append(f"{res} {days}일")
    logger.info(f"\n".join(lic))
    return await ctx.send((f" \n".join(lic)))

@verify.error
async def verify_error(error, i: discord.Interaction):
    error_function(error, i)

@restoreSetting.error
async def set_error(error, i: discord.Interaction):
    error_function(error, i)

async def botRun():
    await bot.start(setting().token)

asyncio.run(botRun())
