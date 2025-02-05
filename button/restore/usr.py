import discord, aiohttp
from function import refreshToken, DB

async def usrRestore(instance, i: discord.Interaction, btnMSG, users):
    await btnMSG.delete()
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
    await instance.btn(111)