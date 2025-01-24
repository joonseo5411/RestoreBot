from quart import Quart
from quart import request
from quart import render_template
import threading

from ouath2 import *

from db import DB

import setting

app = Quart('Restore')

@app.route("/")
async def main():
    return "<h1>Hello, World!</h1>"

@app.route("/callback")
async def callback():
    """Callback User Data"""
    code = request.args.get('code')
    state = int(request.args.get('state'))

    task = [
        exchange_code(code, f"{setting.base_url}/callback"),
        serverCheck(state),
        getIp()
    ]

    exchangeRes, guild, ip = await asyncio.gather(*task)
    print(exchangeRes)

    if not exchangeRes:
        return render_template('error.html', title='인증 실패', ERROR_MSG=""), 404
    
    userInfo = getUserProfile(exchangeRes['access_token'])
    if not userInfo:
        return render_template('error.html', title='인증 실패', ERROR_MSG=''), 500
    
    if not guild:
        return render_template('error.html', title='인증 실패', ERROR_MSG=''), 400
    
    if userInfo == None:
        return render_template('error.html', title='인증 실패', ERROR_MSG=''), 400
    
    await DB.add_user(userInfo['id'], exchangeRes['refresh_token'], state)
    


app.run(host="0.0.0.0", port=4404)