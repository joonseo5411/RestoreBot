from .db import DB

from discord.ext import commands
import discord

class settingBtn:
    def __init__(self, i: discord.Interaction):
        self.i = i
    
    async def btn(self):
        data = await DB.getGuildInfo(self.i.guild_id)
        self.data = data
        print(data)
        class SetBtn(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)

            @discord.ui.button(label="역할설정", emoji="🔰", style=discord.ButtonStyle.blurple)
            async def roleSetting(self, i: discord.Interaction, btn: discord.ui.Button):
                bot = []
                for usr in i.guild.members:
                    if usr.bot:
                        bot.append(usr.name)

                role = []
                for r in i.guild.roles:
                    if not r.name in bot:
                        role.append([r.name, r.id])

                embed = discord.Embed(title='role setting', color=discord.Color.green())
                for btn in range(len(role)):
                    embed.add_field(name=f"{btn}", value=role[btn][0], inline=True)

                class setr0le(discord.ui.View):
                    def __init__(self):
                        super().__init__(timeout=None)

                    @discord.ui.button(label="역할설정", emoji="🔰", style=discord.ButtonStyle.blurple)
                    async def setRole(self, i: discord.Interaction, btn: discord.ui.Button):
                        class roleModal(discord.ui.Modal, title = "🔰 Select role number"):
                            num = discord.ui.TextInput(
                                label="choose role number",
                                style=discord.TextStyle.short,
                                placeholder="1"
                            )

                            async def on_submit(self, interaction: discord.Interaction):
                                # try:
                                num = self.num
                                print(num)
                                num = int(num)
                                print(num)
                                    
                                # except: return await interaction.response.send_message("only integer", ephemeral=True)
                                
                                if not role[num][1]:
                                    return await interaction.response.send_message("unkown role number", ephemeral=True)
                                result = await DB.set_role(role[num][1], interaction.guild_id)
                                return await interaction.response.send_message("seccussful", ephemeral=True)
                        await i.response.send_modal(roleModal())
                await i.response.send_message(embed=embed, view=setr0le(), ephemeral=True)


            @discord.ui.button(label="웹훅설정", emoji="💬", style=discord.ButtonStyle.blurple)
            async def webhookSetting(self, i: discord.Interaction, btn: discord.ui.Button):
                pass

        role = self.i.guild.get_role(int(data[2])) if data[2] != None else False
        webhook = eval(data[1])
        roleName = "설정필요" if not role else role.name
        roleID = "설정필요"if not role else role.id
        webhook = '설정필요' if not webhook[0] else webhook[0]

        embed = discord.Embed(
            title="복구봇 설정하기",
            description=f"🔰ㅣ역할\n```ansi\n🔰 [2;32m설정된 역할[0m: {roleName}\n🔰 [2;32m[2;33m역할 아이디[0m[2;32m[0m: {roleID}\n```\n💬ㅣ웹훅\n```ansi\n💬 [2;34m인증로그[0m: {webhook}\n```",
            color=discord.Color.green()
        )

        await self.i.response.send_message(embed=embed, view=SetBtn(), ephemeral=True)
        self.response = await self.i.original_response()