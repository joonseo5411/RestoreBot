import discord, asyncio
from function import DB
from urllib.request import Request, urlopen

from function import create_category

async def serverRestore(instance, i: discord.Interaction, btnMSG, backupKey):
    await btnMSG.delete()

    class restoreBtn(discord.ui.View):
        def __init__(self, instance, backupKey):
            super().__init__(timeout=None)
            self.instance = instance
            self.backupKey = backupKey

        @discord.ui.button(label="확인했습니다.", emoji="✅", style=discord.ButtonStyle.green)
        async def check(self, i: discord.Interaction, btn: discord.ui.Button):
            data = await DB.getBackupData(self.backupKey)
            if not data:
                return await i.response.send_message(content="없는 데이터입니다.")

            await i.response.send_message(content="복구중")

            await i.guild.edit(community=False)

            # Delete all existing channels
            for channel in i.guild.channels:
                try:
                    await channel.delete()
                except Exception:
                    pass

            # Delete all existing roles
            for role in i.guild.roles:
                try:
                    await role.delete()
                except Exception:
                    pass

            # Restore roles
            roles_data = eval(data[4])
            role_map = {}
            for role_data in reversed(roles_data):
                permissions_dict = {perm_name: True for perm_name in role_data['permissions']}
                if role_data['name'] == "@everyone":
                    role = discord.utils.get(i.guild.roles, name="@everyone")  # Use Discord utilities to get the @everyone role
                    if not role:
                        continue

                    await role.edit(permissions=discord.Permissions(**permissions_dict))
                    role_map[role_data['name']] = role  # Ensure correct assignment to role_map

                else:
                    created_role = await i.guild.create_role(
                        name=role_data['name'],
                        permissions=discord.Permissions(**permissions_dict),
                        color=discord.Color(role_data['color']) if role_data.get('color') else discord.Color.default()
                    )
                    role_map[role_data['name']] = created_role

            guildData = eval(data[2])
            usrAgent = {'User-Agent': 'Mozilla/5.0'}
            icon = urlopen(Request(guildData['icon'], headers=usrAgent)).read() if 'icon' in guildData else None
            banner = urlopen(Request(guildData['banner'], headers=usrAgent)).read() if 'banner' in guildData else None

            await i.guild.edit(icon=icon, name=guildData['name'])

            try:
                await i.guild.edit(banner=banner)
            except Exception:
                dm = await i.user.create_dm()
                embed = discord.Embed(
                    title="⚠️ㅣ경고 발생",
                    description="> 서버의 부스트 레벨이 부족합니다. 서버 부스트를 2단계 이상을 하여 해제 하여 주세요.",
                    color=discord.Color.orange()
                )
                await dm.send(embed=embed)

            try:
                updateChannel = None
                ruleChannel = None
                if "COMMUNITY" in guildData['features']:
                    updateChannel = await i.guild.create_text_channel(name="임시업데이트")
                    ruleChannel = await i.guild.create_text_channel(name="임시규칙")
                    await i.guild.edit(
                        community=True,
                        public_updates_channel=updateChannel,
                        rules_channel=ruleChannel
                    )
            except discord.errors.Forbidden as e:
                dm = await i.user.create_dm()
                embed = discord.Embed(
                    title="⚠️ㅣ에러 발생",
                    description="> 서버의 보안 수준을 높혀야 됩니다. 다음과 같은 에러를 해결 하기 위해 아래의 해결법을 사용 해 주세요.",
                    color=discord.Color.red()
                )
                await dm.send(embed=embed)
                return print(f"Error: {e}")
            
            asyncVar = []
            # Restore channels and messages
            for category in eval(data[3]):
                asyncVar.append(create_category().start(
                    i, category,
                    guildData['rules_channel'], guildData['public_updates_channel'],
                    ruleChannel, updateChannel, role_map))

            await asyncio.gather(*asyncVar)

    embed = discord.Embed(
        title="사직하기 앞서...",
        description="- 봇 역할을 젤 위로 해주세요.\n- 반드시 관리자 권한을 부여 해 주세요.",
        color=discord.Color.orange()
    )
    embed.set_footer(text="Zita Restore", icon_url="https://i.imgur.com/X2gz8W2.png")
    embed.set_image(url="https://i.imgur.com/zAyZwj6.png")
    await i.response.send_message(embed=embed, view=restoreBtn(instance, backupKey), ephemeral=True)