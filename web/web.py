from quart import Quart
from quart import request
from quart import render_template

from ouath2 import exchange_code

import setting

app = Quart('Restore')

@app.route("/")
async def main():
    return "<h1>Hello, World!</h1>"

@app.route("/callback")
async def callback():
    """Callback User Data"""
    code = request.args.get('code')
    state = request.args.get('state')

    exchangeRes = await exchange_code(code, f"{setting.base_url}/callback")



    if not exchangeRes:
        return render_template('error.html', title='인증 실패', ERROR_MSG=""), 404
    


def run():
    app.run(host="0.0.0.0", port=4404, debug=False)