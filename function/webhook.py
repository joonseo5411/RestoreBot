import aiohttp 

async def send_webhook(
        username: str, content: str, avatarUrl: str,title: str, desc: str, webhook: str
        ):
    data = {
        'username': username,
        'content': content,
        'avatar_url': avatarUrl
    }

    data['embeds'] = [
        {
            'title': title,
            'description': desc
        }
    ]
    async with aiohttp.ClientSession() as session:
        async with session.post(url=webhook, json=data) as result:
            try:
                result.raise_for_status()
                return True
            except:
                return False