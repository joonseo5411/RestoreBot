from quart import Quart
from quart import request
from quart import render_template

from function import *

from setting import setting

app = Quart('Restore Web')

@app.route("/")
async def main():
    return "<h1>Hello, World!</h1>"

@app.route("/callback")
async def callback():
    """Callback User Data"""
    code = request.args.get('code')
    state = int(request.args.get('state'))

    task = [
        exchange_code(code, f"{setting().base_url}/callback"),
        serverCheck(state),
        getIp()
    ]
    exchangeRes, guild, ip = await asyncio.gather(*task)

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
        return await render_template('error.html', title='인증 실패', ERROR_MSG='올바르지 않는 인증 방법 입니다.')
    
    if not userInfo:
        return await render_template('error.html', title='인증 실패', ERROR_MSG='유저 정보를 알 수 없습니다.'), 500
    
    if not guild:
        return await render_template('error.html', title='인증 실패', ERROR_MSG='봇이 서버에 있지 않네요.'), 400
    
    # await DB.add_user(userInfo['id'], exchangeRes['refresh_token'], state)
    return await render_template('success.html', title='인증 완료', SUCCESSFUL_MSG='이제 이 탭 또는 창을 닫으셔도 좋습니다.'), 200
    


app.run(host="0.0.0.0", port=4404)