import json
import os

class setting:
    def __init__(self):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '//설정.json'), 'r') as file:
            data = json.load(file)
            self.token = data['botToken']
            self.base_url = data['domain']
            self.admin_id = data['adminID']
            self.api_endpoint = data['apiEndpoint']
            self.client_id = data['clientID']
            self.client_secret = data['clientSecret']
            self.botweb = data['restoreWebhook']
            self.timeZone = data['timeZone']