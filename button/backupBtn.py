import discord
from function import DB
import asyncio

class backupBtn(discord.ui.View):
    def __init__(self, instance, interaction_message):
        super().__init__(timeout=None)
        self.instance = instance
        self.interaction_message = interaction_message

    @discord.ui.button(label="확인했습니다.", emoji="✅", style=discord.ButtonStyle.blurple)
    async def check(self, i: discord.Interaction, btn: discord.ui.Button):
        embed = discord.Embed(
            title="👥 백업 진행중", description=">>> 현재 백업을 진행 하고 있습니다.\n최대 **__2시간__**이 걸릴 수 있습니다.",
            color=discord.Color.orange()
        )
        await i.response.send_message(embed=embed)
        await self.interaction_message.delete()
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