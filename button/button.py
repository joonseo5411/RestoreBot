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
from .inviteBtn import customInviteCallback

import aiohttp, pytz, asyncio, discord, time

class settingBtn:
    def __init__(self, i: discord.Interaction):
        self.i = i
    
    async def btn(self, editMSG=None):
        data, backup, invite = await DB.getGuildInfo(self.i.guild_id)
        data = [str([]), str([False, False]), None, False, False, False] if not data else data
        invite = [False, False, False] if not invite else invite
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
            
            @discord.ui.button(label="복구하기", style=discord.ButtonStyle.green, emoji="👥", row=1)
            async def restoreUsr(self, i: discord.Interaction, btn: discord.ui.Button):
                return await restoreUser(self.instance, i)
                       
            
            @discord.ui.button(label="백업하기", style=discord.ButtonStyle.green, emoji="👥", row=1)
            async def storeUsr(self, i: discord.Interaction, btn: discord.ui.Button):
                return await backupCallback(self.instance, i, data)


            @discord.ui.button(label="커스텀 초대링크 만들기", style=discord.ButtonStyle.grey, emoji="📥", row=2)
            async def customInviteLink(self, i: discord.Interaction, btn: discord.ui.Button):
                return await customInviteCallback(self.instance, i, data, invite)

            @discord.ui.button(label="라이센스 연장/등록", row=3, style=discord.ButtonStyle.red, emoji="⏰")
            async def addLicense(self, i: discord.Interaction, btn: discord.ui.Button):
                return await i.response.send_modal(registerModal(self.instance))

        role = self.i.guild.get_role(int(data[2])) if data[2] != None else False
        usr = len(eval(data[0]))
        webhook = eval(data[1])
        roleName = "설정필요" if not role else role.name
        roleID = "설정필요" if not role else role.id
        webhook = '설정필요' if not webhook[0] else webhook[0]
        KST = pytz.timezone(setting().timeZone)
        expireDate = '등록필요' if not data[4] else datetime.fromtimestamp(data[4]).astimezone(KST).strftime("%Y-%m-%d %H:%M")
        leastBackup = "백업필요" if not backup else datetime.fromtimestamp(backup[1]).astimezone(KST).strftime("%Y-%m-%d %H:%M")
        inviteName = '설정필요' if not invite[1] else invite[1]
        inviteLink = '설정필요' if not invite[2] else invite[2]

        embed = discord.Embed(
            title="복구봇 설정하기",
            description=f"""🔰ㅣ역할 ```ansi
🔰 [2;32m설정된 역할[0m: {roleName}
🔰 [2;32m[2;33m역할 아이디[0m[2;32m[0m: {roleID}```
💬ㅣ웹훅 ```ansi
💬 [2;34m인증로그[0m: {webhook}```
📥ㅣ초대설정 ```ansi
📥 [2;32m설정된 이름[0m: {inviteName}
📥 [2;32m[2;33m설정된 초대주소[0m[2;32m[0m: {inviteLink}```
⚙️ㅣ부가정보 ```ansi
⏰ [2;31m남은시간[0m: {expireDate}
👥 [2;32m마지막 백업일[0m: {leastBackup}
👥 [2;34m복구인원[0m: {usr}명```""",
            color=discord.Color.green()
        )

        if editMSG == None:
            await self.i.response.send_message(embed=embed, view=SetBtn(self), ephemeral=True)
            self.response = await self.i.original_response()
        else:
            await self.response.edit(embed=embed, view=SetBtn(self))