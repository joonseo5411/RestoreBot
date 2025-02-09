import discord
from function import DB

async def serverRestore(instance, i: discord.Interaction, btnMSG):
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
                ctg = await i.guild.create_category(category[0])
                for channel in category[1]:
                    if channel[1] == "text":
                        chanel = await ctg.create_text_channel(name=channel[0])
                    
                    if channel[1] == "voive":
                        chanel = await ctg.create_voice_channel(name=channel[0])

                    if channel[1] == "news":
                        chanel = await ctg.create_text_channel(name=channel[0], news=True)

                    if channel[1] == "forum":
                        chanel = await ctg.create_forum(name=channel[0])

                    for msg in category[2][2]:
                        wbhook = await chanel.create_webhook()
                        await wbhook.send(username=msg[0], avatar_url=msg[1], content=msg[2], embeds=msg[3])

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