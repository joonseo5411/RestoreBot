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
            
            @discord.ui.button(label="라이센스 연장/등록", row=2, style=discord.ButtonStyle.green, emoji="⏰")
            async def addLicense(self, i: discord.Interaction, btn: discord.ui.Button):
                return await i.response.send_modal(registerModal(self.instance))
            
            @discord.ui.button(label="복구하기", style=discord.ButtonStyle.green, emoji="👥", row=1)
            async def restoreUsr(self, i: discord.Interaction, btn: discord.ui.Button):
                return await restoreUser(self.instance, i)
                       
            
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
                        await self.instance.btn(1)
                
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
