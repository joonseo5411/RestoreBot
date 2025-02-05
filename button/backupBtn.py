import discord
from function import DB
import asyncio

async def backupCallback(instance, i: discord.Interaction, data: list):
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

    await i.response.send_message(embed=embed, view=backupBtn(instance), ephemeral=True)
    interactionMessage = await i.original_response()