import aiohttp 

async def send_webhook(
        session, username: str, content: str, avatarUrl: str,title: str, desc: str, webhook: str
        ):
    data = {
        'username': username,
        'content': content,
        'avatar_url': avatarUrl
    }

    data['embeds'] = [
        {
            'title': title,
            'description': desc,
            "footer": {
                "text": "Zita Restore",
                "icon_url": "https://i.imgur.com/X2gz8W2.png"
            },
        }
    ]
    try:
        async with session.post(url=webhook, json=data) as result:
            result.raise_for_status()
            return
    except:
        return