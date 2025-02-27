import discord

from function import DB
from .usr import usrRestore
from .server import serverRestore

async def restoreUser(instance, i: discord.Interaction):
    class restoreUsr(discord.ui.Modal, title='👥ㅣ복구하기'):
        licenseVar = discord.ui.TextInput(
            label='복구키를 입력 해 주세요.',
            style=discord.TextStyle.short,
            placeholder='1s3w5', max_length=5, min_length=5
        )

        def __init__(self, instance):
            super().__init__()
            self.instance = instance

        async def on_submit(self, i: discord.Interaction):
            recover_key = str(self.licenseVar)
            users = await DB.getRestoreKey(recover_key)

            if users == False:
                return await i.response.send_message(
                    embed=discord.Embed(
                        title=":warning: 존재 하지 않는 복구키", description="- 올바르게 하였는데도 문제 발생하면 고객센터에 문의해주세요.", color=discord.Color.red()
                    ), ephemeral = True
                )

            class restoreBtn(discord.ui.View):
                def __init__(self, instance):
                    super().__init__(timeout=None)
                    self.instance = instance

                @discord.ui.button(label="유저복구", emoji="👥", style=discord.ButtonStyle.green)
                async def usrRestore(self, i: discord.Interaction, btn: discord.ui.Button):
                    return await usrRestore(self.instance, i, btnMSG, users)
                    
                @discord.ui.button(label="서버복구", emoji='🏀', style=discord.ButtonStyle.red)
                async def serverRestore(self, i: discord.Interaction, btn: discord.ui.Button):
                    return await serverRestore(self.instance, i, btnMSG, recover_key)

            await i.response.send_message(view=restoreBtn(self.instance), ephemeral=True)
            btnMSG = await i.original_response()
    await i.response.send_modal(restoreUsr(instance))