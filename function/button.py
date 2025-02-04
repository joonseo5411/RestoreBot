from .db import DB

from discord.ext import commands
from datetime import datetime
from .logger import logger
from .setting import setting
from .oauth2 import refreshToken, addUser

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
                await i.response.send_message(embed=embed, view=setr0le(self.instance), ephemeral=True)
                msg = await i.original_response()
                return


            @discord.ui.button(label="웹훅설정", emoji="💬", style=discord.ButtonStyle.blurple)
            async def webhookSetting(self, i: discord.Interaction, btn: discord.ui.Button):
                if not data[4]:
                    embed = discord.Embed(title=":warning: 연장/등록 필요", description="- 라이센스가 만료 되어있네요. 연장 해 주세요.", color=discord.Color.red())
                    return await i.response.send_message(embed=embed, ephemeral=True)
                
                class webhookBtn(discord.ui.View):
                    def __init__(self, instance):
                        super().__init__(timeout=None)
                        self.instance = instance

                    @discord.ui.button(label="이 체널에 웹훅설정하기", emoji="💬", style=discord.ButtonStyle.green)
                    async def thisChannelSetWebhook(self, i: discord.Interaction, btn: discord.ui.Button):
                        wbhook = await i.channel.create_webhook(name="Verify LOG")
                        wbhook = wbhook.url
                        await DB.set_webhook([wbhook, webhook[1]], i.guild_id)
                        await msg.delete()
                        await i.response.send_message(content="- 웹훅 설정을 완료 하였어요.", ephemeral=True)
                        return await self.instance.btn(1)

                    @discord.ui.button(label="다른 체널에 웹훅설정하기", emoji="💬", style=discord.ButtonStyle.red, row=1)
                    async def otherChannelSetWebhook(self, i: discord.Interaction, btn: discord.ui.Button):
                        wbhook = await i.channel.create_webhook(name="Verify LOG")
                        class wbhookModal(discord.ui.Modal, title = "💬ㅣ웹훅설정"):
                            wbhook = discord.ui.TextInput(
                                label="웹후크 URI를 적어주세요.",
                                style=discord.TextStyle.short,
                                placeholder="웹후크 URI"
                            )

                            def __init__(self, instance):
                                super().__init__()
                                self.instance = instance

                            async def on_submit(self, interaction: discord.Interaction):
                                wbhook = str(self.wbhook)
                                await DB.set_webhook([wbhook, webhook[1]], interaction.guild_id)
                                await msg.delete()
                                await interaction.response.send_message(content="- 웹훅 설정을 완료 하였어요.", ephemeral=True)
                                return await self.instance.btn(1)
                        return await i.response.send_modal(wbhookModal(self.instance))
                await i.response.send_message(view=webhookBtn(self.instance), ephemeral=True)
                msg = await i.original_response()
                return
            
            @discord.ui.button(label="라이센스 연장/등록", row=2, style=discord.ButtonStyle.green, emoji="⏰")
            async def addLicense(self, i: discord.Interaction, btn: discord.ui.Button):
                class registerModal(discord.ui.Modal, title='⏰ㅣ연장/등록하기'):
                    licenseVar = discord.ui.TextInput(
                        label='라이센스 키를 입력 해 주세요.',
                        style=discord.TextStyle.short,
                        placeholder='1s3w5-1f3df-1cvbs-qwert',
                        max_length=23,
                        min_length=23
                    )

                    def __init__(self, instance):
                        super().__init__()
                        self.instance = instance

                    async def on_submit(self, interaction: discord.Interaction):
                        registers = await DB.registerGuild(int(i.guild_id), str(self.licenseVar))
                        if not registers:
                            embed = discord.Embed(title='라이센스 등록 실패',
                                description='- 시도하신 라이센스를 확인 하시고 다시 이용 해 주시길 바랍니다.',
                                color=discord.Color.red())
                            embed.set_footer(text=f"Zita Restore", icon_url=f"https://i.imgur.com/X2gz8W2.png")
                            return await interaction.response.send_message(embed=embed, ephemeral=True)

                        embed = discord.Embed(
                            title="라이센스 등록/연장 성공",
                            description="- `/설정`을 통해 설정을 마무리 해 주세요.\n- `/인증`명령어를 통해 인증 임베드를 출력 가능합니다.",
                            color=discord.Color.green()
                        )
                        embed.set_footer(text=f"Zita Restore", icon_url=f"https://i.imgur.com/X2gz8W2.png")
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        await self.instance.btn(1)
                        if registers != True:
                            dm = await i.user.create_dm()
                            embed1 = discord.Embed(title="Restore Service", description=f">>> 복구키는 `{registers}`입니다.\n-# 이 키는 저장 하거나 기억 해두세요.", color=discord.Color.green())
                            embed1.set_footer(text="Zita Restore", icon_url="https://i.imgur.com/X2gz8W2.png")
                            await dm.send(embed=embed1)
                return await i.response.send_modal(registerModal(self.instance))
            
            @discord.ui.button(label="복구하기", style=discord.ButtonStyle.green, emoji="👥", row=1)
            async def restoreUsr(self, i: discord.Interaction, btn: discord.ui.Button):
                if not data[4]:
                    embed = discord.Embed(title=":warning: 연장/등록 필요", description="- 라이센스가 만료 되어있네요. 연장 해 주세요.", color=discord.Color.red())
                    return await i.response.send_message(embed=embed, ephemeral=True)

                class restoreBtn(discord.ui.View):
                    def __init__(self, instance):
                        super().__init__(timeout=None)
                        self.instance = instance

                    @discord.ui.button(label="유저복구", emoji="👥", style=discord.ButtonStyle.green)
                    async def usrRestore(self, i: discord.Interaction, btn: discord.ui.Button):
                        await btnMSG.delete()
                        class restoreUser(discord.ui.Modal, title='👥ㅣ복구하기'):
                            licenseVar = discord.ui.TextInput(
                                label='복구키를 입력 해 주세요.',
                                style=discord.TextStyle.short,
                                placeholder='1s3w5',
                                max_length=5,
                                min_length=5
                            )

                            def __init__(self, instance):
                                super().__init__()
                                self.instance = instance

                            async def on_submit(self, i: discord.Interaction):
                                recover_key = str(self.licenseVar)
                                users = await DB.getRestoreKey(recover_key)

                                if not users:
                                    return await i.response.send_message(
                                        embed=discord.Embed(
                                            title=":warning: 존재 하지 않는 복구키", description="- 올바르게 하였는데도 문제 발생하면 고객센터에 문의해주세요.\n- 인원이 0명일 경우, 이런 문구가 뜹니다.", color=discord.Color.red()
                                        ), ephemeral = True
                                    )

                                await i.response.send_message(
                                    embed=discord.Embed(
                                        title="👥 유저 복구중...", description="- 유저를 **복구** 중입니다.\n- 최대 **__2시간__**이 소요 될 수 있습니다.", color=discord.Color.orange()
                                    ).set_footer(text="Zita Restore", icon_url="https://i.imgur.com/X2gz8W2.png")
                                )
                                msg = await i.original_response()
                                usrs = users if len(users) < 3 else [users[i:i+round(len(users)/2)] for i in range(0, len(users), round(len(users)/2))]
                                async with aiohttp.ClientSession() as session:
                                    newUsr = []
                                    async def asyncRestore(user):
                                        for user in user:
                                            user_id = user[0]
                                            refresh_token = user[1]
                                            new_token = await refreshToken(session, refresh_token)
                                            if new_token == False:
                                                return

                                            new_refresh = new_token["refresh_token"]
                                            new_token = new_token["access_token"]

                                            newUsr.append([new_refresh, user_id])
                                            await addUser(session, new_token, i.guild.id, user_id)
                                    
                                    if len(users) > 3:
                                        await asyncio.gather(asyncRestore(usrs[0]), asyncRestore(usrs[1]))
                                    else: 
                                        await asyncRestore(users)
                                    await DB.changeRefreshToken(users, newUsr)


                                await msg.edit(
                                    embed=discord.Embed(
                                        title="👥 유저 복구완료", description="- 유저를 **복구**완료 했습니다.", color=discord.Color.green()
                                    ).set_footer(text="Zita Restore", icon_url="https://i.imgur.com/X2gz8W2.png")
                                )
                                await self.instance.btn(111)
                        await i.response.send_modal(restoreUser(self.instance))
                    @discord.ui.button(label="서버복구", emoji='🏀', style=discord.ButtonStyle.red)
                    async def serverRestore(self, i: discord.Interaction, btn: discord.ui.Button):
                        await btnMSG.delete()
                        class restoreBtn(discord.ui.View):
                            def __init__(self, instance):
                                super().__init__(timeout=None)
                                self.instance = instance
                            
                            @discord.ui.button(label="확인했습니다.", emoji="✅", style=discord.ButtonStyle.green)
                            async def check(self, i: discord.Interaction, btn: discord.ui.Button):
                                data = await DB.getBackupData(i.guild_id)
                                if not data:
                                    return
                                # 모든 채널 삭제
                                for channel in i.guild.channels:
                                    try:
                                        await channel.delete()
                                    except:
                                        pass

                                # 모든 역할 삭제
                                for role in i.guild.roles:
                                    try:
                                        await role.delete()
                                    except:
                                        pass

                                for role in eval(data[4]):
                                    if "@everyone" in role:
                                        continue
                                    await i.guild.create_role(name=data[0], permissions=data[2], color=data[1])

                                # 채널 복구 및 메시지 복구
                                for category in eval(data[3]):
                                    await i.guild.create_category(category[0], overwrites=category[1])
                                
                        
                        embed = discord.Embed(
                            title="사직하기 앞서...",
                            description="- 봇 역할을 젤 위로 해주세요.\n- 반드시 관리자 권한을 부여 해 주세요.",
                            color=discord.Color.orange()
                        )
                        embed.set_footer(text="Zita Restore", icon_url="https://i.imgur.com/X2gz8W2.png")
                        embed.set_image(url="https://i.imgur.com/zAyZwj6.png")
                        await i.response.send_message(embed=embed, view=restoreBtn(self.instance), ephemeral=True)

                await i.response.send_message(view=restoreBtn(self.instance), ephemeral=True)
                btnMSG = await i.original_response()
            
            @discord.ui.button(label="백업하기", style=discord.ButtonStyle.green, emoji="👥", row=1)
            async def storeUsr(self, i: discord.Interaction, btn: discord.ui.Button):
                if not data[4]:
                    embed = discord.Embed(title=":warning: 연장/등록 필요", description="- 라이센스가 만료 되어있네요. 연장 해 주세요.", color=discord.Color.red())
                    return await i.response.send_message(embed=embed, ephemeral=True)

                class backupBtn(discord.ui.View):
                    def __init__(self, instance):
                        super().__init__(timeout=None)
                        self.instance = instance
                    
                    @discord.ui.button(label="확인했습니다.", emoji="✅", style=discord.ButtonStyle.blurple)
                    async def check(self, i: discord.Interaction, btn: discord.ui.Button):
                        embed = discord.Embed(
                            title="👥 백업 진행중", description=">>> 현재 백업을 진행 하고 있습니다.\n최대 **__2시간__**이 걸릴 수 있습니다.",
                            color=discord.Color.orange()
                        )
                        await i.response.send_message(embed=embed)
                        await interactionMessage.delete()
                        msg = await i.original_response()

                        # 길드 관련 백업
                        guildData = [i.guild.name, i.guild.icon, i.guild.banner]

                        # 채널 및 카테고리 백업
                        async def channelBackup():
                            channelVar = []
                            for category in i.guild.categories:
                                thisChannel = []
                                for channel in category.channels:
                                    try:
                                        async for msg in channel.history(limit=100):
                                            thisChannel.append([
                                                msg.author.global_name if msg.author.global_name != None else msg.author.name,
                                                msg.author.avatar, msg.content if msg.content != '' else msg.embeds])
                                        thisChannel = [[channel.name], thisChannel]
                                    except:
                                        pass
                                    
                                    
                                    for overwrite in channel.overwrites:
                                        for perm in overwrite.permissions:
                                            print(perm)
                                channelVar.append([category.name, thisChannel])
                            return channelVar

                        # 역할 백업
                        async def roleBackup():
                            roleData = []
                            for role in i.guild.roles:
                                perm = []
                                for rolePerm in role.permissions:
                                    if not rolePerm[1]:
                                        continue
                                    perm.append([rolePerm])
                                roleData.append([role.name, role.colour, perm])
                            return roleData

                        # 이모지 백업
                        async def emojiBackup():
                            emojidata = []
                            for emoji in i.guild.emojis:
                                emojidata.append([emoji.name, emoji.url])
                            return emojidata

                        channels, roles, emojidata = await asyncio.gather(channelBackup(), roleBackup(), emojiBackup())

                        await DB.backupServer(guildData, channels, roles, emojidata, i.guild_id)
                        await msg.edit(embed=discord.Embed(
                            title="👥 백업완료", description=">>> 백업을 완료 하였습니다.", color=discord.Color.green()
                        ))
                        await self.instance.btn(111)
                
                embed = discord.Embed(
                    title="사직하기 앞서...",
                    description="- 봇 역할을 젤 위로 해주세요.\n- 반드시 관리자 권한을 부여 해 주세요.",
                    color=discord.Color.orange()
                )
                embed.set_footer(text="Zita Restore", icon_url="https://i.imgur.com/X2gz8W2.png")
                embed.set_image(url="https://i.imgur.com/zAyZwj6.png")

                await i.response.send_message(embed=embed, view=backupBtn(self.instance), ephemeral=True)
                interactionMessage = await i.original_response()

                

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


# ('create_instant_invite', True)
# ('kick_members', False)
# ('ban_members', False)
# ('administrator', False)
# ('manage_channels', False)
# ('manage_guild', False)
# ('add_reactions', True)
# ('view_audit_log', False)
# ('priority_speaker', False)
# ('stream', True)
# ('read_messages', True)
# ('send_messages', True)
# ('send_tts_messages', False)
# ('manage_messages', False)
# ('embed_links', True)
# ('attach_files', True)
# ('read_message_history', True)
# ('mention_everyone', False)
# ('external_emojis', True)
# ('view_guild_insights', False)
# ('connect', True)
# ('speak', True)
# ('mute_members', False)
# ('deafen_members', False)
# ('move_members', False)
# ('use_voice_activation', True)
# ('change_nickname', True)
# ('manage_nicknames', False)
# ('manage_roles', False)
# ('manage_webhooks', False)
# ('manage_expressions', False)
# ('use_application_commands', True)
# ('request_to_speak', True)
# ('manage_events', False)
# ('manage_threads', False)
# ('create_public_threads', True)
# ('create_private_threads', True)
# ('external_stickers', True)
# ('send_messages_in_threads', True)
# ('use_embedded_activities', True)
# ('moderate_members', False)
# ('view_creator_monetization_analytics', False)
# ('use_soundboard', True)
# ('create_expressions', False)
# ('create_events', False)
# ('use_external_sounds', True)
# ('send_voice_messages', True)
# ('send_polls', True)
# ('use_external_apps', True)
# ('create_instant_invite', False)
# ('kick_members', False)
# ('ban_members', False)
# ('administrator', False)
# ('manage_channels', False)
# ('manage_guild', False)
# ('add_reactions', False)
# ('view_audit_log', False)
# ('priority_speaker', False)
# ('stream', False)
# ('read_messages', False)
# ('send_messages', False)
# ('send_tts_messages', False)
# ('manage_messages', True)
# ('embed_links', False)
# ('attach_files', False)
# ('read_message_history', True)
# ('mention_everyone', False)
# ('external_emojis', False)
# ('view_guild_insights', False)
# ('connect', False)
# ('speak', False)
# ('mute_members', False)
# ('deafen_members', False)
# ('move_members', False)
# ('use_voice_activation', False)
# ('change_nickname', False)
# ('manage_nicknames', False)
# ('manage_roles', False)
# ('manage_webhooks', False)
# ('manage_expressions', False)
# ('use_application_commands', False)
# ('request_to_speak', False)
# ('manage_events', False)
# ('manage_threads', False)
# ('create_public_threads', False)
# ('create_private_threads', False)
# ('external_stickers', False)
# ('send_messages_in_threads', False)
# ('use_embedded_activities', False)
# ('moderate_members', False)
# ('view_creator_monetization_analytics', False)
# ('use_soundboard', False)
# ('create_expressions', False)
# ('create_events', False)
# ('use_external_sounds', False)
# ('send_voice_messages', False)
# ('send_polls', False)
# ('use_external_apps', False)
