import urllib.request, cgi, json, urllib.parse

server_address = "http://localhost:7001"


class Player:

    def __init__(self):
        self.ore_quantity = None
        self.delta_ore = None
        self.health = None
        self._id = None
        self.world = None

        self.join()
        self.send_state()

    def join(self):
        endpoint = '/join'
        settings = {
            'sendState': 'false'
        }
        settings = '?' + urllib.parse.urlencode(settings)
        final_url = server_address + endpoint + settings
        response = json.loads(urllib.request.urlopen(final_url).read().decode(encoding='UTF-8'))
        self._id = response.get('id', '')

    def send_state(self):
        endpoint = '/sendState'
        settings = {
            'id': self._id
        }
        settings = '?' + urllib.parse.urlencode(settings)
        final_url = server_address + endpoint + settings
        response = json.loads(urllib.request.urlopen(final_url).read().decode(encoding='UTF-8'))
        self.world = response.get('world', '')

    def action(self, _action):
        endpoint = '/action'
        settings = {
            'id': self._id,
            'action': _action,
            'sendState': 'true'
        }
        settings = '?' + urllib.parse.urlencode(settings)
        final_url = server_address + endpoint + settings
        response = json.loads(urllib.request.urlopen(final_url).read().decode(encoding='UTF-8'))
        self.world = response.get('world', '')
        self.ore_quantity = response.get('vitals', dict()).get('ore_quantity')
        self.delta_ore = response.get('vitals', dict()).get('delta_ore')
        self.health = response.get('vitals', dict()).get('health')

player = Player()
player.action('w')
