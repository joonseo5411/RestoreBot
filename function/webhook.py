import requests 

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
    result = requests.post(url=webhook, json=data)

    try:
        result.raise_for_status()
        return True
    except requests.exceptions.HTTPError:
        return False
    else:
        return False