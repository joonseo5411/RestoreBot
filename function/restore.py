import discord, asyncio
from function import DB
from urllib.request import Request, urlopen

class create_category:
    def __init__(self):
        self.isRuleChannel = {}
        self.isUpdateChannel = {}

    async def start(self,
            i: discord.Interaction, category: dict,
            rules_channel, public_updates_channel,
            tmp_rule, tmp_update, role_map):
        ctg = await i.guild.create_category(category['category_name'])

        category_permissions = []
        for perm in category['category_permissions']:
            role_name = perm.get('role_name')
            if role_name in role_map:
                permissions = {perm_name: True for perm_name in perm.get('permissions', [])}
                category_permissions.append((role_map[role_name], discord.PermissionOverwrite(**permissions)))

        await ctg.edit(overwrites=dict(category_permissions))

        ruleChannel = None
        publicUpdateChannel = None

        self.isRuleChannel[i.guild_id] = tmp_rule
        self.isUpdateChannel[i.guild_id] = tmp_update

        for channel in category['channels']:
            await restore_message(
                i, channel, ctg, category_permissions, rules_channel, public_updates_channel,
                tmp_rule, tmp_update, role_map)

    async def restore_message(self, i: discord.Interaction, channel: dict, ctg, category_permissions, rules_channel, public_updates_channel, tmp_rule, tmp_update, role_map):
        discord_channel = None
        if channel['type'] == "text":
            discord_channel = await ctg.create_text_channel(name=channel['name'])
            
            if str(rules_channel) == str(channel['name']):
                await i.guild.edit(community=True, rules_channel=discord_channel, public_updates_channel=self.isUpdateChannel[i.guild_id])
                await tmp_rule.delete()
                isRuleChannel[i.guild_id] = discord_channel


            if str(public_updates_channel) == str(channel['name']):
                await i.guild.edit(community=True, rules_channel=self.isRuleChannel[i.guild_id], public_updates_channel=discord_channel)
                await tmp_update.delete()
                isUpdateChannel[i.guild_id] = discord_channel

        elif channel['type'] == "news":
            discord_channel = await ctg.create_text_channel(name=channel['name'], news=True)
        elif channel['type'] == "voice":
            discord_channel = await ctg.create_voice_channel(name=channel['name'])
        elif channel['type'] == "forum":
            discord_channel = await ctg.create_forum(name=channel['name'])

        if discord_channel:
            if (len(channel['permissions']) == 0 or
                channel['permissions'] == [perm for perm, _ in category_permissions]):
                await discord_channel.edit(sync_permissions=True)
            else:
                channel_overwrites = {}
                for perm in channel['permissions']:
                    role_name = perm.get('role_name')
                    if role_name in role_map:
                        permissions = {perm_name: True for perm_name in perm.get('permissions', [])}
                        channel_overwrites[role_map[role_name]] = discord.PermissionOverwrite(**permissions)

                await discord_channel.edit(overwrites=channel_overwrites if channel_overwrites else dict(category_permissions))

            wbhook = await discord_channel.create_webhook(name='BackupWebhook')
            for msg in reversed(channel['messages']):
                embeds = []
                for embed_data in msg['embeds']:
                    embed_color = embed_data.get('color')
                    embed = discord.Embed(
                        title=embed_data.get('title'),
                        description=embed_data.get('description'),
                        color=discord.Color(embed_color) if embed_color is not None else discord.Color.default()
                    )
                    
                    # Set footer if present
                    if 'footer' in embed_data and embed_data['footer']:
                        embed.set_footer(
                            text=embed_data['footer'][0] or "",
                            icon_url=embed_data['footer'][1] or ""
                        )
                    
                    # Set author if present
                    if 'author' in embed_data and embed_data['author']:
                        embed.set_author(
                            name=embed_data['author'][0] or "",
                            url=embed_data['author'][1] or "",
                            icon_url=embed_data['author'][2] or ""
                        )
                    
                    # Add image and thumbnail if present
                    if 'image' in embed_data and embed_data['image']:
                        embed.set_image(url=embed_data['image'])
                    
                    if 'thumbnail' in embed_data and embed_data['thumbnail']:
                        embed.set_thumbnail(url=embed_data['thumbnail'])
                    
                    # Add fields if any
                    for field in embed_data.get('fields', []):
                        embed.add_field(
                            name=field['name'],
                            value=field['value'],
                            inline=field.get('inline', False)
                        )
                    
                    embeds.append(embed)
                try:
                    await wbhook.send(
                        username=msg['author'],
                        avatar_url=msg['avatar'],
                        content=msg['content'],
                        embeds=embeds
                    )
                except:
                    pass
            await wbhook.delete()