# Do not touch key
english={
    'commands': {
        'register': ['register', 'To register guild'],
        'setRole': ['set_role', 'To set guild verify role'],
        'setWebhook': ['set_webhook', 'To send guild verify webhook'],
        'sendButton': ['send_button', 'To send verify button on this channel'],
        'checkLicense': ['license', 'To check expire date and license key']
    },
    'embed': {
        'register':{
            'success': ['success to register this guild!', 'Use `help` command to checking command list', 0x008000],
            'fail': ['fail to register this guild!', 'Check your license key and use command later', 0xFF0000]
        },
        'setRole':{
            'success': ['success to set role', '- Current role: {rolemention}({role})\n- role id: {roleid}', 0x008000],
            'fail': ['fali to set role', 'Check your role and use command later', 0xFF0000]
        },
        'sendButton':{
            'success': ['to send button', 'Successful to send button', 0x008000],
            'wait': ['Sending button ', 'Sending button verify...', 0xFFA500]
        },
        'checkLicense': ['check license', '- LIcense key: ||{licenseKey}||\n- Expire date: {date}', 0x008000],
        'setWebhook':['success to set role', '- Currnet webhook url: {webhook}', 0x008000],
        'NotFoundLicense': ['usage restrictions', 'You cannot it because you do not have a license.', 0xFF0000]
    }
}