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
            guildData = {
                "name": i.guild.name,
                "icon": str(i.guild.icon),
                "banner": str(i.guild.banner),
                "features": i.guild.features,
                "rules_channel": i.guild.rules_channel.name if i.guild.rules_channel else None,
                "public_updates_channel": i.guild.public_updates_channel.name if i.guild.public_updates_channel else None
            }

            bot_names = [bot.global_name or bot.name for bot in i.guild.members if bot.bot]

            # 채널 및 카테고리 백업
            async def channelBackup():
                channel_data = []

                for category in i.guild.categories:
                    category_permissions = []
                    for role, overwrite in category.overwrites.items():
                        if not isinstance(role, discord.Role):
                            continue
                        permissions = [perm for perm, value in overwrite if value]
                        category_permissions.append({
                            "role_name": role.name,
                            "permissions": permissions
                        })

                    category_data = []

                    for channel in category.channels:
                        try:
                            channel_permissions = []
                            if isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
                                if channel.permissions_synced:
                                    channel_permissions = category_permissions
                                else:
                                    for role, overwrite in channel.overwrites.items():
                                        if not isinstance(role, discord.Role):
                                            continue
                                        permissions = [perm for perm, value in overwrite if value]
                                        channel_permissions.append({
                                            "role_name": role.name,
                                            "permissions": permissions
                                        })

                                channel_messages = []
                                if isinstance(channel, discord.TextChannel):
                                    async for msg in channel.history(limit=100):
                                        # Gather embeds
                                        embeds = [
                                            {
                                                "title": embed.title or None,
                                                "description": embed.description or None,
                                                "color": int(embed.color.value) if embed.color else None,
                                                "image": embed.image.url if embed.image else None,
                                                "thumbnail": embed.thumbnail.url if embed.thumbnail else None,
                                                "footer": [
                                                    embed.footer.text or None,
                                                    str(embed.footer.icon_url) if embed.footer.icon_url else None
                                                ],
                                                "author": [
                                                    embed.author.name if embed.author and embed.author.name else None,
                                                    str(embed.author.url) if embed.author and embed.author.url else None,
                                                    str(embed.author.icon_url) if embed.author and embed.author.icon_url else None
                                                ],
                                                "fields": [
                                                    {"name": field.name, "value": field.value, "inline": field.inline}
                                                    for field in embed.fields
                                                ]
                                            }
                                            for embed in msg.embeds
                                        ]

                                        # Collect attachment URLs if any
                                        attachment_urls = [attachment.url for attachment in msg.attachments if attachment.url]

                                        # Append URLs to content or use only URLs if no content
                                        message_content = msg.content or ""
                                        if attachment_urls:
                                            message_content += "\n" + "\n".join(attachment_urls)

                                        channel_messages.append({
                                            "author": msg.author.global_name or msg.author.name,
                                            "avatar": msg.author.avatar.url if msg.author.avatar else None,
                                            "content": message_content,
                                            "embeds": embeds
                                        })

                                # Append channel data
                                channel_type = "news" if (isinstance(channel, discord.TextChannel) and channel.is_news()) else str(channel.type)
                                
                                category_data.append({
                                    "name": channel.name,
                                    "type": channel_type,
                                    "permissions": channel_permissions,
                                    "messages": channel_messages
                                })

                        except Exception as e:
                            print(f"Error backing up channel {channel.name}: {e}")

                    channel_data.append({
                        "category_name": category.name,
                        "category_permissions": category_permissions,
                        "channels": category_data
                    })

                return channel_data

            # 역할 백업
            async def roleBackup():
                role_data = []
                for role in i.guild.roles:
                    if role.name not in bot_names:
                        permissions = [perm[0] for perm in role.permissions if perm[1]]
                        role_data.append({
                            "name": role.name,
                            "color": int(role.color.value) if int(role.color.value) != 0 else None,
                            "permissions": permissions
                        })
                return role_data

            # 이모지 백업
            async def emojiBackup():
                return [{"name": emoji.name, "url": str(emoji.url)} for emoji in i.guild.emojis]

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