import asyncio
import html
import json
import requests
import websockets
import os
import Smelter

connected = set()


def path_to_this_files_directory():
	dir_path = os.path.dirname(os.path.realpath(__file__))
	return dir_path + '/'


# Generate whitelisted_words set
with open(path_to_this_files_directory() + 'settings.json') as json_data:
	d = json.load(json_data)

erebus_address = d.get('productionErebusAddress', '') if d.get('inProduction', False) else d.get(
	'developmentErebusAddress', '')
server_port = d.get('serverPort', 7005)
public_address = 'localhost'

smelter = Smelter.Smelter()
print("Whitelist includes {} words".format((smelter.number_of_whitelisted_words())))


def dumps(obj: dict):
	try:
		return json.dumps(obj)
	except:
		return "{}"


def loads(obj: str):
	try:
		return json.loads(obj)
	except:
		return {}


def get_username(aid):
	url = '{api_url}/users/{aid}/username'.format(api_url=erebus_address, aid=aid)
	req = requests.get(url).json()
	return req


async def handler(websocket, path):
	global connected
	# Register.
	connected.add(websocket)
	try:
		# Implement logic here.
		aid = None
		username = None
		while True:
			message = await websocket.recv()
			if aid is None:
				if message[:10] == '/register ':
					erebus_response = get_username(message[10:])
					if erebus_response.get('valid_aid', False):
						username = erebus_response.get('username', '')
						aid = message[10:]
						await websocket.send(dumps({
							'author': 'Synergy',
							'color': 'red',
							'authenticated': True,
							'message': 'Welcome to And/Ore. Official Accounts have red names.'
						}))
					else:
						await websocket.send(dumps({
							'author': 'Synergy',
							'color': 'red',
							'authenticated': False,
							'message': "Invalid aid"
						}))
				else:
					await websocket.send(dumps({
						'author': 'Synergy',
						'color': 'red',
						'message': "You must send over an aid first"
					}))
			else:
				if message[:6] == '/chat ':
					await asyncio.wait([ws.send(dumps({
						'author': username,
						'color': 'green',
						'message': html.escape(smelter.filter_sentence(message[6:]))
					})) for ws in connected])
				else:
					await websocket.send(json.dumps({
						'author': 'Synergy',
						'color': 'red',
						'message': 'Unknown command "{}"'.format(html.escape(message))
					}))
	finally:
		# Unregister.
		connected.remove(websocket)


print("Running Synergy on port {}".format(server_port))
start_server = websockets.serve(handler, public_address, server_port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
