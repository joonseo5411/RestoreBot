from .db import DB

from discord.ext import commands
import discord

class settingBtn:
    def __init__(self, i: discord.Interaction, bot: commands.Bot):
        self.bot = bot
        self.i = i

    async def btn(self):
        data = await DB.getGuildInfo(self.i.guild_id)
        self.data = data
        print(data)
        class roleBtn(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)

            @discord.ui.button(label="ㅣ역할설정", emoji="🔰", style=discord.ButtonStyle.blurple)
            async def roleSetting(self, i: discord.Interaction, btn: discord.ui.Button):
                pass

            @discord.ui.button(label="ㅣ웹훅설정", emoji="💬", style=discord.ButtonStyle.blurple)
            async def webhookSetting(self, i: discord.Interaction, btn: discord.ui.Button):
                pass
            
        embed = discord.Embed(
            title="복구봇 설정하기",
            description=f"🔰ㅣ역할\n```ansi\n🔰 [2;32m설정된 역할[0m: {roleName}\n🔰 [2;32m[2;33m역할 아이디[0m[2;32m[0m: {roleID}\n```\n💬ㅣ웹훅\n```ansi\n💬 [2;34m인증로그[0m: {'설정필요' if not data[1][0] else data[1][0]}\n```",
            color=discord.Color.green()
        )

    async def roleSetting(self):
        pass