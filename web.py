from quart import Quart, request, render_template

from function import *
import time

app = Quart('Restore Web')

settingVar = setting()

@app.route("/")
async def main():
    return await render_template('error.html', title='404', ERROR_MSG='잘못 들어 온 것 같아요. 다시 확인 후, 접속 해 주세요.'), 404

@app.route("/callback")
async def callback():
    if not {'code', 'state'} <= request.args.keys():
        return await render_template('error.html', title='인증 실패', ERROR_MSG="잘못된 접근 입니다."), 404

    code = str(request.args.get('code'))
    state = int(request.args.get('state'))

    async with aiohttp.ClientSession() as session:
        exchangeRes, guild, ip = await asyncio.gather(
            exchange_code(session, code, f"{settingVar.base_url}/callback"),
            getGuild(session, state),
            getIp(session, request)
        )

        if not exchangeRes:
            return await render_template('error.html', title='인증 실패', ERROR_MSG="존재하지 않는 callback 토큰 입니다."), 404

        if "Unknown Guild" in str(guild):
            return await render_template('error.html', title='인증 실패', ERROR_MSG='봇이 서버에 있지 않네요.'), 400

        userInfo = await getUserProfile(session, exchangeRes['access_token'])
        if not userInfo and not 'email' in userInfo:
            return await render_template('error.html', title='인증 실패', ERROR_MSG='유저 정보를 알 수 없습니다.'), 500

        usrlogger.info(f"{ip[0]} Users in data email: {userInfo['email']}, User: {userInfo['global_name']}({userInfo['id']}) in guild: {state}")

        role_id, webhook = await DB.add_user(int(userInfo['id']), exchangeRes['refresh_token'], state)
        if not role_id:
            return await render_template('error.html', title='인증 실패', ERROR_MSG='등록 되지 않는 서버입니다.'), 400

        role = {'name': '설정 필요', 'id': '설정 필요'}

        if role_id != "None":
            roleName = next((role['name'] for role in guild['roles'] if role['id'] == str(role_id)), "없음")

        task = [
            giveRoleToMember(session, state, int(userInfo['id']), role_id),
            send_webhook(session, 'Zita Restore', None, "https://i.imgur.com/X2gz8W2.png", f"{userInfo['global_name']}({userInfo['id']})", f"""
> 유저가 정상적으로 인증을 완료 하였습니다.

>>> ⏰ 인증 날짜: <t:{int(time.time())}:f>
🌐 인증 서버: {guild['name']}({state})
🔰 역할 정보: {roleName}({role_id})
""", webhook),
            send_webhook(session, 'Zita Restore', None, "https://i.imgur.com/X2gz8W2.png", '인증 정보', f"""### -# > {userInfo['global_name']}({userInfo['id']}) 님의 정보입니다.
🌐 유저 IP 정보```ansi
🌐[2;31m유저 아이피[0m: [2;30m{ip[0]}[0m
🌐[2;32m유저 통신사[0m: [2;30m{ip[1]}[0m
🌐[2;33m예상 지역[0m: [2;30m{ip[2]}[0m
🌐[2;34m유저 국가[0m: [2;30m{ip[3]}[0m```
👤  유저 정보```ansi
👤 [2;31m인증 서버[0m: [2;30m{guild['name']}({state})
👤 [2;32m부여된 역할[0m: [0m[2;30m{roleName}({role_id})[0m```
""", "https://discord.com/api/webhooks/1334443562007396423/R82BgBWOZBJmqmHmIPZYN3QVd6GzPeFYmvp1rcC77lu5Cu2o6zVR0NoVx4yJmfKHIRNz")
        ]

        await asyncio.gather(*task)
        return await render_template('success.html', title='인증 완료', SUCCESSFUL_MSG='이제 이 탭 또는 창을 닫으셔도 좋습니다.'), 200

app.run(host="0.0.0.0", port=4404, use_reloader=False)
