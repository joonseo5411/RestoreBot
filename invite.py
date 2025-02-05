from quart import Quart, request, render_template, redirect
from function import *
from datetime import timedelta

import aiohttp, time, asyncio

app = Quart('Invite Web')

settingVar = setting()

redirect_url = "https://invite.zita.kr"


@app.route("/")
async def main():
    return await render_template('error.html', title='404', ERROR_MSG='잘못 들어 온 것 같아요. 다시 확인 후, 접속 해 주세요.'), 404

@app.route("/callback")
async def callback():
    if not {'code', 'state'} <= request.args.keys():
        return await render_template('error.html', title='가입 실패', ERROR_MSG="잘못된 접근 입니다."), 404

    code = str(request.args.get('code'))
    state = str(request.args.get('state'))

    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://discord.com/api/v9/invites/{state}?with_counts=true&with_expiration=true&with_permissions=false') as response:
            data = await response.json()
        guildID = data['guild']['id']

        exchangeRes, guild, ip = await asyncio.gather(
            exchange_code(session, code, f"{redirect_url}/callback"),
            getGuild(session, guildID),
            getIp(session, request)
        )

        if not exchangeRes:
            return await render_template('error.html', title='가입 실패', ERROR_MSG="존재하지 않는 callback 토큰 입니다."), 404

        if "Unknown Guild" in guild:
            return await render_template('error.html', title='가입 실패', ERROR_MSG='봇이 서버에 있지 않네요.'), 400

        userInfo = await getUserProfile(session, exchangeRes['access_token'])
        if not userInfo and not 'email' in userInfo:
            return await render_template('error.html', title='가입 실패', ERROR_MSG='유저 정보를 알 수 없습니다.'), 500

        logger.info(f"{ip[0]} Users in data email: {userInfo['email']}, User: {userInfo['global_name']}({userInfo['id']}) in guild: {guildID}")

        role_id, webhook = await DB.add_user(int(userInfo['id']), exchangeRes['refresh_token'], guildID)
        if not role_id:
            return await render_template('error.html', title='가입 실패', ERROR_MSG='등록 되지 않는 서버입니다.'), 400

        role = {'name': '설정 필요', 'id': '설정 필요'}

        if role_id != "None":
            roleName = next((role['name'] for role in guild['roles'] if role['id'] == str(role_id)), "없음")

        await addUser(session, exchangeRes['access_token'], guildID, userInfo['id'])

        task = [
            giveRoleToMember(session, guildID, int(userInfo['id']), role_id),
            send_webhook(session, 'Zita Restore', None, "https://i.imgur.com/X2gz8W2.png", f"{userInfo['global_name']}({userInfo['id']})", f"""
> 유저가 정상적으로 인증을 완료 하였습니다.

>>> ⏰ 인증 날짜: <t:{int(time.time())}:f>
👥 인증 링크: https://discord.gg/{state}
🌐 인증 서버: {guild['name']}({guildID})
🔰 역할 정보: {roleName}({role_id})
""", webhook),
            send_webhook(session, 'Zita Restore', None, "https://i.imgur.com/X2gz8W2.png", '인증 정보', f"""### -# > {userInfo['global_name']}({userInfo['id']}) 님의 정보입니다.
🌐 유저 IP 정보```ansi
🌐[2;31m유저 아이피[0m: [2;30m{ip[0]}[0m
🌐[2;32m유저 통신사[0m: [2;30m{ip[1]}[0m
🌐[2;33m예상 지역[0m: [2;30m{ip[2]}[0m
🌐[2;34m유저 국가[0m: [2;30m{ip[3]}[0m```
👤  유저 정보```ansi
👤 [2;31m인증 링크[0m: [2;30mhttps://discord.gg/{state}
👤 [2;31m인증 서버[0m: [2;30m{guild['name']}({guildID})
👤 [2;32m부여된 역할[0m: [0m[2;30m{roleName}({role_id})[0m```
""", "https://discord.com/api/webhooks/1334443562007396423/R82BgBWOZBJmqmHmIPZYN3QVd6GzPeFYmvp1rcC77lu5Cu2o6zVR0NoVx4yJmfKHIRNz")
        ]

        await asyncio.gather(*task)
        return await render_template('success.html', title='가입 완료', SUCCESSFUL_MSG='이제 이 탭 또는 창을 닫으셔도 좋습니다.'), 200

        

@app.route("/<inviteLink>", methods=['GET', 'POST'])
async def invite(inviteLink):
    if inviteLink == "callback":
        return
    try:
        if request.method == "GET":
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://discord.com/api/v9/invites/{inviteLink}?with_counts=true&with_expiration=true&with_permissions=false') as response:
                    data = await response.json()
                    guildID = data['guild']['id']

                    checkGuild = await serverCheck(session, guildID)
                    if not checkGuild:
                        return await render_template('error.html', title='400', ERROR_MSG='길드에 봇이 없는 것 같네요.'), 400

                    members = data['approximate_member_count']
                    onlines = data['approximate_presence_count']
                    server_image = f'https://cdn.discordapp.com/icons/{guildID}/{data['guild']['icon']}.png?size=128' if data['guild']['icon'] else None
                    BANNER = f'https://cdn.discordapp.com/banners/{guildID}/{data['guild']['banner']}.png?size=1024' if data['guild']['banner'] else server_image
                    guild_name = data['guild']['name']
                    return await render_template('invite.html', guild_name=guild_name, onlines=onlines, members=members, server_image=server_image, BANNER=BANNER, POST=f'/{inviteLink}')
        if request.method == "POST":
            return redirect(f"https://discord.com/oauth2/authorize?client_id=1324642750028578816&response_type=code&redirect_uri=https%3A%2F%2Finvite.zita.kr%2Fcallback&scope=identify+email+guilds.join&state={inviteLink}")
    except:
        return await render_template('error.html', title="알수 없는 애러", ERROR_MSG="접근이 잘못 된 것 같네요."), 404

app.run(host="0.0.0.0", port=4405, use_reloader=False)
