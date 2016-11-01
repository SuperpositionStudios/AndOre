from child_game import world as world_py
import asyncio
import json
import requests
import websockets
import datetime

import logging
logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

erebus_address = 'http://localhost:7004'
sleipnir_address = 'ws://localhost:7100'
public_address = 'localhost'
port = 7101

connected = set()
sleipnir_connection = None


def message_sleipnir(endpoint, data):
    req = requests.post(sleipnir_address + endpoint, json=data)
    node_response = req.json()
    if node_response['Successful_Request'] is False:
        print('Failed to message master node with {data}'.format(data=str(data)))


def new_message_sleipnir(data: dict):
    sleipnir_connection.send(dumps(data))

World = world_py.World

world = world_py.World(sleipnir_address, new_message_sleipnir)
world.spawn_ore_deposits(5)


class Client:

    def __init__(self, connection):
        aid = None
        username = None
        authenticated = None
        connection = connection


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
    req = requests.get('http://localhost:7004/get/username', params={'aid': aid}).json()
    return req


def tick_server_if_needed():
    now = datetime.datetime.now()
    if (now - world.last_tick).microseconds >= world.microseconds_per_tick:
        world.tick()


async def game_client(websocket, path):
    global connected
    global world
    # Register.
    client = Client(websocket)
    connected.add(client)
    try:
        # Implement logic here.
        aid = None
        username = None
        authenticated = False
        while True:
            request = await websocket.recv()
            tick_server_if_needed()
            request = loads(request)

            print(request)
            if authenticated:
                if request.get('request', None) == 'action':
                    action = request.get('action', '')
                    world.players[aid].action(action)
                    world_view = world.players[aid].world_state()
                    inventory = world.players[aid].corp.render_inventory()
                    vitals = world.players[aid].get_vitals()

                    await websocket.send(dumps({
                        'authenticated': authenticated,
                        'request': 'sendState',
                        'world': world_view,
                        'inventory': inventory,
                        'vitals': vitals
                    }))
                elif request.get('request', None) == 'send_state':
                    world_view = world.players[aid].world_state()
                    inventory = world.players[aid].corp.render_inventory()
                    vitals = world.players[aid].get_vitals()

                    await websocket.send(dumps({
                        'authenticated': authenticated,
                        'request': 'sendState',
                        'world': world_view,
                        'inventory': inventory,
                        'vitals': vitals
                    }))
            else:
                if request.get('request', None) == 'register':
                    aid = request.get('aid', '')
                    erebus_response = get_username(aid)
                    if erebus_response.get('valid_aid', False):
                        username = erebus_response.get('username', '')
                        authenticated = True
                        await websocket.send(dumps({
                            'authenticated': authenticated,
                            'message': 'Welcome to Panagoul'
                        }))
                    else:
                        await websocket.send(dumps({
                            'authenticated': authenticated,
                            'message': "Invalid aid"
                        }))
                else:
                    await websocket.send(dumps({
                        'authenticated': authenticated,
                        'message': "You must register your connection!"
                    }))
    finally:
        # Unregister.
        connected.remove(websocket)


async def sleipnir_client():
    global sleipnir_connection
    async with websockets.connect(sleipnir_address) as websocket:
        try:
            sleipnir_connection = websocket

            await websocket.send(dumps({
                'request': 'register',
                'type': 'node',
                'name': 'Toivo',
                'public_address': 'ws://localhost:7101'
            }))

            while True:
                request = await websocket.recv()
                request = loads(request)
                request_type = request.get('request', None)
                if request_type == 'player_enter':
                    player_corp_id = request.get('cid')
                    player_aid = request.get('aid')
                    corp_ore_quantity = request.get('coq', 0)
                    new_player_obj = world.new_player(player_id=player_aid, corp_id=player_corp_id, corp_ore_quantity=corp_ore_quantity)
                elif request_type == 'update_values':
                    response = request.get('data', {})
                    world.update_values(response)

        finally:
            print("Connection to sleipnir closed")

print("Running Synergy on port {}".format(port))
start_server = websockets.serve(game_client, public_address, port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_until_complete(sleipnir_client())
asyncio.get_event_loop().run_forever()
