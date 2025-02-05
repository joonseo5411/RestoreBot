from function import DB

import discord, aiohttp

async def customInviteCallback(instance, i: discord.Interaction, data: list, invite: list):
    class inviteModal(discord.ui.Modal, title='📥커스텀 초대 설정'):
        inviteName = discord.ui.TextInput(
            label="📥ㅣ커스텀 초대 이름 설정",
            placeholder="Zita",
            default=None if not invite[1] else invite[1]
        )

        inviteLink = discord.ui.TextInput(
            label="📥ㅣ초대 링크 설정",
            placeholder="https://discord.gg/7UNfBGmX",
            default=None if not invite[2] else invite[2]
        )

        def __init__(self, instance):
            super().__init__()
            self.instance = instance

        async def on_submit(self, i: discord.Interaction):
            inviteName = str(self.inviteName).replace(" ", "-")
            inviteLink = str(self.inviteLink).split('/')[-1]

            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://discord.com/api/v9/invites/{inviteLink}?with_counts=true&with_expiration=true&with_permissions=false") as response:
                    data = await response.json()
                    if 'Unknown Invite' in str(data):
                        embed = discord.Embed(title="📥 커스텀 링크 에러", description="- 서버 링크가 잘못 된 것 같네요.", color=discord.Color.red())
                        return await i.response.send_message(embed=embed, ephemeral=True)

                    if str(data['guild']['id']) != str(i.guild_id):
                        embed = discord.Embed(title="📥 커스텀 링크 에러", description="- 서버 링크랑 등록 시도한 서버랑 같지 않네요.", color=discord.Color.red())
                        return await i.response.send_message(embed=embed, ephemeral=True)

                    await DB.updateInvite(inviteName, inviteLink, i.guild_id)
                    embed = discord.Embed(title="📥 커스텀 링크 등록 완료", description=f"- [여기](https://invite.zita.kr/{inviteName})를 눌러 확인이 가능합니다.", color=discord.Color.green())                    
                    await i.response.send_message(embed=embed, ephemeral=True)
                    return await self.instance.btn(1)

    return await i.response.send_modal(inviteModal(instance))