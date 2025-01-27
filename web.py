from quart import Quart
from quart import request
from quart import render_template

from function import *

from function import setting

app = Quart('Restore Web')

@app.route("/")
async def main():
    return await render_template('error.html', title='404', ERROR_MSG='잘못 들어 온 것 같아요. 다시 확인 후, 접속 해 주세요.'), 404

@app.route("/callback")
async def callback():
    """Callback User Data"""
    code = request.args.get('code')
    state = int(request.args.get('state'))

    task = [
        serverCheck(state),
        getIp()
    ]
    exchangeRes = await exchange_code(code, f"{setting().base_url}/callback")
    guild, ip = await asyncio.gather(*task)

    if not exchangeRes:
        return await render_template('error.html', title='인증 실패', ERROR_MSG="존재하지 않는 callback 토큰 입니다."), 404
    
    infoTask = [
        getIpInfo(ip),
        getUserProfile(exchangeRes['access_token'])
    ]
    try:
        ipInfo, userInfo = await asyncio.gather(*infoTask)
        logger.info(f"{ip} Users in data email: {userInfo['email']}, User: {userInfo['global_name']}({userInfo['id']}) in guild: {state}")
    except:
        return await render_template('error.html', title='인증 실패', ERROR_MSG='올바르지 않는 인증 방법 입니다.'), 400
    
    if not userInfo:
        return await render_template('error.html', title='인증 실패', ERROR_MSG='유저 정보를 알 수 없습니다.'), 500
    
    if not guild:
        return await render_template('error.html', title='인증 실패', ERROR_MSG='봇이 서버에 있지 않네요.'), 400
    
    try:
        role_id, webhook = await DB.add_user(int(userInfo['id']), exchangeRes['refresh_token'], state)
    except:
        return await render_template('error.html', title='인증실패', ERROR_MSG='등록 되지 않는 서버입니다.'), 400
    async def sendWebhook():
        if not webhook:
            return
        await send_webhook('verify logger', None, None, 'verify', '```ansi\ntest')
    task = [
        giveRoleToMember(state, int(userInfo['id']), role_id),
        sendWebhook()
    ]
    await asyncio.gather(*task)
    return await render_template('success.html', title='인증 완료', SUCCESSFUL_MSG='이제 이 탭 또는 창을 닫으셔도 좋습니다.'), 200
    


app.run(host="0.0.0.0", port=4404, use_reloader=False)