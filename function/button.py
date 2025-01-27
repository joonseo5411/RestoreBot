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

            @discord.ui.button(label="", emoji="", style=discord.ButtonStyle.blurple)
            async def roleSetting(self, i: discord.Interaction, btn: discord.ui.Button):
                pass

            @discord.ui.button(label="", emoji="", style=discord.ButtonStyle.blurple)
            async def webhookSetting(self, i: discord.Interaction, btn: discord.ui.Button):
                pass
            
        embed = discord.Embed(
            title="설정",
            description="",
            color=discord.Color.green()
        )

    async def roleSetting(self):
        pass