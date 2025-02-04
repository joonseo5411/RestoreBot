from discord import Interaction
from discord.ui import Button

from function import DB
import discord

async def roleCallback(instance, i: Interaction, data: list):
    if not data[4]:
        embed = discord.Embed(title=":warning: 연장/등록 필요", description="- 라이센스가 만료 되어있네요. 연장 해 주세요.", color=discord.Color.red())
        return await i.response.send_message(embed=embed, ephemeral=True)

    bot = []
    for usr in i.guild.members:
        if usr.bot:
            bot.append(usr.name)

    role = []
    for r in i.guild.roles:
        if not r.name in bot:
            role.append([r.name, r.id])

    embed = discord.Embed(title='역할 설정', description="> 아래의 있는 번호를 확인후 번호를 작성 하여 주세요.", color=discord.Color.green())
    for btn in range(len(role)):
        embed.add_field(name=f"{btn}. {role[btn][0]}", value=f"-# 역할 설정을 누른 후,\n-# `{btn}`을(를) 입력 해 주세요.", inline=True)

    class setr0le(discord.ui.View):
        def __init__(self, instance):
            super().__init__(timeout=None)
            self.instance = instance

        @discord.ui.button(label="역할설정", emoji="🔰", style=discord.ButtonStyle.blurple)
        async def setRole(self, i: discord.Interaction, btn: discord.ui.Button):
            class roleModal(discord.ui.Modal, title = "🔰ㅣ역할설정"):
                num = discord.ui.TextInput(
                    label="역할 번호를 선택 해 주세요.",
                    style=discord.TextStyle.short,
                    placeholder="1"
                )

                def __init__(self, instance):
                    super().__init__()
                    self.instance = instance

                async def on_submit(self, interaction: discord.Interaction):
                    num = self.num
                    try: num = int(str(num))
                    except: return await interaction.response.send_message("- 숫자만 가능해요.", ephemeral=True)
                    
                    try: roleID = role[num][1]
                    except: return await interaction.response.send_message("- 역할을 설정 할수 없는 숫자네요.\n- 다시 확인 후 시도 해 주세요.", ephemeral=True)

                    await DB.set_role(roleID, interaction.guild_id)
                    await msg.delete()
                    await interaction.response.send_message(content="- 변경을 **완료** 했어요.", ephemeral=True)
                    return await self.instance.btn(1)
            await i.response.send_modal(roleModal(self.instance))
    await i.response.send_message(embed=embed, view=setr0le(instance), ephemeral=True)
    msg = await i.original_response()
    return