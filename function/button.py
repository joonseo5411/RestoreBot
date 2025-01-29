from .db import DB

from discord.ext import commands
import discord

from datetime import datetime
from .setting import setting
import pytz

class settingBtn:
    def __init__(self, i: discord.Interaction):
        self.i = i
    
    async def btn(self):
        data = await DB.getGuildInfo(self.i.guild_id)
        data = [str([]), str([False, False]), None, False, False, False] if not data else data
        class SetBtn(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)

            @discord.ui.button(label="역할설정", emoji="🔰", style=discord.ButtonStyle.blurple)
            async def roleSetting(self, i: discord.Interaction, btn: discord.ui.Button):
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
                    def __init__(self):
                        super().__init__(timeout=None)

                    @discord.ui.button(label="역할설정", emoji="🔰", style=discord.ButtonStyle.blurple)
                    async def setRole(self, i: discord.Interaction, btn: discord.ui.Button):
                        class roleModal(discord.ui.Modal, title = "🔰ㅣ역할설정"):
                            num = discord.ui.TextInput(
                                label="역할 번호를 선택 해 주세요.",
                                style=discord.TextStyle.short,
                                placeholder="1"
                            )

                            async def on_submit(self, interaction: discord.Interaction):
                                num = self.num
                                try: num = int(str(num))
                                except: return await interaction.response.send_message("- 숫자만 가능해요.", ephemeral=True)
                                
                                try: roleID = role[num][1]
                                except: return await interaction.response.send_message("- 역할을 설정 할수 없는 숫자네요.\n- 다시 확인 후 시도 해 주세요.", ephemeral=True)

                                await DB.set_role(roleID, interaction.guild_id)
                                await msg.edit(content="- 성공적으로 변경을 완료 했어요.", embed=None, view=None)
                                return await interaction.response.send_message(content="- `/설정` 명령어를 통해 변경된 내용을 볼 수 있어요.", ephemeral=True)
                        await i.response.send_modal(roleModal())
                await i.response.send_message(embed=embed, view=setr0le(), ephemeral=True)
                msg = await i.original_response()


            @discord.ui.button(label="웹훅설정", emoji="💬", style=discord.ButtonStyle.blurple)
            async def webhookSetting(self, i: discord.Interaction, btn: discord.ui.Button):
                if not data[4]:
                    embed = discord.Embed(title=":warning: 연장/등록 필요", description="- 라이센스가 만료 되어있네요. 연장 해 주세요.", color=discord.Color.red())
                    return await i.response.send_message(embed=embed, ephemeral=True)
             
                class wbhookModal(discord.ui.Modal, title = "💬ㅣ웹훅설정"):
                    wbhook = discord.ui.TextInput(
                        label="웹후크 URI를 적어주세요.",
                        style=discord.TextStyle.short,
                        placeholder="웹후크 URI"
                    )

                    async def on_submit(self, interaction: discord.Interaction):
                        wbhook = str(self.wbhook)
                        await DB.set_webhook([wbhook, webhook[1]], interaction.guild_id)
                        return await interaction.response.send_message(content="- 성공적으로 설정을 완료 했어요.\n- `/설정` 명령어를 통해 변경된 내용을 볼 수 있어요.", ephemeral=True)
                return await i.response.send_modal(wbhookModal())
            
            @discord.ui.button(label="라이센스 연장/등록", row=1, style=discord.ButtonStyle.green, emoji="⏰")
            async def addLicense(self, i: discord.Interaction, btn: discord.ui.Button):
                class registerModal(discord.ui.Modal, title='⏰ㅣ연장/등록하기'):
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
                                title="라이센스 등록/연장 성공",
                                description="- `/설정`을 통해 설정을 마무리 해 주세요.\n- `/인증`명령어를 통해 인증 임베드를 출력 가능합니다.",
                                color=discord.Color.green()
                            )
                        embed.set_footer(text=f"Zita Restore", icon_url=f"https://cdn.discordapp.com/attachments/1317512746702733362/1322530302282956852/17.png?ex=67996b93&is=67981a13&hm=8d47a02d4943f4088678439522b2ce960c06b09679ef653624135cf0b6eb7318&")
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                return await i.response.send_modal(registerModal())
            
            @discord.ui.button(label="복구하기", style=discord.ButtonStyle.green, emoji="👥", row=1)
            async def restoreUsr(self, i: discord.Interaction, btn: discord.ui.Button):
                if not data[4]:
                    embed = discord.Embed(title=":warning: 연장/등록 필요", description="- 라이센스가 만료 되어있네요. 연장 해 주세요.", color=discord.Color.red())
                    return await i.response.send_message(embed=embed, ephemeral=True)

        role = self.i.guild.get_role(int(data[2])) if data[2] != None else False
        webhook = eval(data[1])
        roleName = "설정필요" if not role else role.name
        roleID = "설정필요" if not role else role.id
        webhook = '설정필요' if not webhook[0] else webhook[0]
        KST= pytz.timezone(setting().timeZone)
        expireDate = '등록필요' if not data[4] else datetime.fromtimestamp(data[4]).astimezone(KST).strftime("%Y-%m-%d %H:%M")

        embed = discord.Embed(
            title="복구봇 설정하기",
            description=f"🔰ㅣ역할\n```ansi\n🔰 [2;32m설정된 역할[0m:\n{roleName}\n🔰 [2;32m[2;33m역할 아이디[0m[2;32m[0m:\n{roleID}\n```\n💬ㅣ웹훅\n```ansi\n💬 [2;34m인증로그[0m:\n{webhook}\n```\n⚙️ 부가정보\n```ansi\n⏰ [2;31m남은시간[0m:\n{expireDate}\n```",
            color=discord.Color.green()
        )

        await self.i.response.send_message(embed=embed, view=SetBtn(), ephemeral=True)
        self.response = await self.i.original_response()