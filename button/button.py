from function import DB

from discord.ext import commands
from datetime import datetime
from function import logger
from function import setting
from function import refreshToken, addUser

from .roleBtn import roleCallback
from .webhookBtn import webhookCallback
from .licenseBtn import registerModal
from .restore import restoreUser
from .backupBtn import backupCallback

import aiohttp, pytz, asyncio, discord, time

class settingBtn:
    def __init__(self, i: discord.Interaction):
        self.i = i
    
    async def btn(self, editMSG=None):
        data, backup = await DB.getGuildInfo(self.i.guild_id)
        data = [str([]), str([False, False]), None, False, False, False] if not data else data
        class SetBtn(discord.ui.View):
            def __init__(self, instance):
                super().__init__(timeout=None)
                self.instance = instance

            @discord.ui.button(label="역할설정", emoji="🔰", style=discord.ButtonStyle.blurple)
            async def roleSetting(self, i: discord.Interaction, btn: discord.ui.Button):
                return await roleCallback(self.instance, i, data)


            @discord.ui.button(label="웹훅설정", emoji="💬", style=discord.ButtonStyle.blurple)
            async def webhookSetting(self, i: discord.Interaction, btn: discord.ui.Button):
                return await webhookCallback(self.instance, i, btn, data, webhook)
            
            @discord.ui.button(label="라이센스 연장/등록", row=2, style=discord.ButtonStyle.red, emoji="⏰")
            async def addLicense(self, i: discord.Interaction, btn: discord.ui.Button):
                return await i.response.send_modal(registerModal(self.instance))
            
            @discord.ui.button(label="복구하기", style=discord.ButtonStyle.green, emoji="👥", row=1)
            async def restoreUsr(self, i: discord.Interaction, btn: discord.ui.Button):
                return await restoreUser(self.instance, i)
                       
            
            @discord.ui.button(label="백업하기", style=discord.ButtonStyle.green, emoji="👥", row=1)
            async def storeUsr(self, i: discord.Interaction, btn: discord.ui.Button):
                return await backupCallback(self.instance, i, data)

        role = self.i.guild.get_role(int(data[2])) if data[2] != None else False
        usr = len(eval(data[0]))
        webhook = eval(data[1])
        roleName = "설정필요" if not role else role.name
        roleID = "설정필요" if not role else role.id
        webhook = '설정필요' if not webhook[0] else webhook[0]
        KST = pytz.timezone(setting().timeZone)
        expireDate = '등록필요' if not data[4] else datetime.fromtimestamp(data[4]).astimezone(KST).strftime("%Y-%m-%d %H:%M")
        leastBackup = "백업필요" if not backup else datetime.fromtimestamp(backup[1]).astimezone(KST).strftime("%Y-%m-%d %H:%M")

        embed = discord.Embed(
            title="복구봇 설정하기",
            description=f"🔰ㅣ역할\n```ansi\n🔰 [2;32m설정된 역할[0m:\n{roleName}\n🔰 [2;32m[2;33m역할 아이디[0m[2;32m[0m:\n{roleID}\n```\n💬ㅣ웹훅\n```ansi\n💬 [2;34m인증로그[0m:\n{webhook}\n```\n⚙️ 부가정보\n```ansi\n⏰ [2;31m남은시간[0m:\n{expireDate}\n👥 [2;32m마지막 백업일[0m:\n{leastBackup}\n👥 [2;34m복구인원[0m:\n{usr}명```",
            color=discord.Color.green()
        )

        if editMSG == None:
            await self.i.response.send_message(embed=embed, view=SetBtn(self), ephemeral=True)
            self.response = await self.i.original_response()
        else:
            await self.response.edit(embed=embed, view=SetBtn(self))