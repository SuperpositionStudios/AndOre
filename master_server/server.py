import asyncio
import json
import requests
import websockets
import master_server_config as config
from typing import Dict, List
import game_classes
import random
import os


def path_to_this_files_directory():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return dir_path + '/'

with open(path_to_this_files_directory() + 'settings.json') as json_data:
    d = json.load(json_data)

in_production = d.get('inProduction', False)

erebus_address = d.get('productionErebusAddress', '') if in_production else d.get('developmentErebusAddress', '')

public_address = 'localhost'
node_port = d.get('nodePort', 7100)
client_port = d.get('playerPort', 7200)

nodes = dict()  # type: Dict[str, Node]
corporations = dict()  # type: Dict[str, game_classes.Corporation]
players = dict()  # type: Dict[str, game_Classes.Player]
connected_players = dict()  # type: Dict[str, PlayerConnection]


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


class Node:

    def __init__(self, connection):
        self.connection = connection
        self.name = None
        self.public_address = None

    def set_name(self, name: str):
        self.name = name

    def set_public_address(self, address: str):
        self.public_address = address


def get_username(aid):
    req = requests.get(erebus_address + '/get/username', params={'aid': aid}).json()
    return req


def get_random_node_name():
    return random.choice(list(nodes.keys()))


async def player(websocket, path):
    global players
    try:
        authenticated = False
        aid = 'None'
        username = 'None'
        current_node = None
        while True:
            request = await websocket.recv()
            request = loads(request)
            #print(request)

            if authenticated:
                if request.get('request', None) == 'join':
                    # check if loaded in a world
                    if aid in players:
                        current_node = players[aid].get_current_node()
                        if current_node in nodes:
                            pass
                        else:
                            current_node = get_random_node_name()
                            players[aid].assign_node(current_node)
                        node_obj = nodes[current_node]
                        await nodes[current_node].connection.send(dumps({
                            'request': 'player_enter',
                            'coq': players[aid].corp.amount_of_ore(),
                            'aid': aid,
                            'cid': players[aid].corp.corp_id
                        }))
                        await websocket.send(dumps({
                            'request': 'update_node',
                            'node_name': node_obj.name,
                            'node_address': node_obj.public_address
                        }))
                    else:
                        new_corp = game_classes.Corporation()
                        if config.developing:
                            new_corp.gain_ore(5000)
                        else:
                            new_corp.gain_ore(205)
                        corporations[new_corp.corp_id] = new_corp
                        current_player = game_classes.Player()
                        current_player.assign_aid(aid)
                        current_player.assign_corp(new_corp)
                        current_player.assign_username(username)
                        current_player.assign_node(get_random_node_name())

                        players[aid] = current_player

                        current_node = players[aid].get_current_node()
                        node_obj = nodes[current_node]

                        await nodes[current_node].connection.send(dumps({
                            'request': 'player_enter',
                            'coq': current_player.corp.amount_of_ore(),
                            'aid': aid,
                            'cid': new_corp.corp_id
                        }))


                        await websocket.send(dumps({
                            'request': 'update_node',
                            'node_name': node_obj.name,
                            'node_address': node_obj.public_address
                        }))
            else:
                if request.get('request', None) == 'register':
                    aid = request.get('aid', 'None')
                    if aid is not 'None':
                        erebus_response = get_username(aid)
                        if erebus_response.get('valid_aid', False):
                            aid = aid
                            username = erebus_response.get('username', 'None')
                            authenticated = True

                            await websocket.send(dumps({
                                'authenticated': authenticated
                            }))
                        else:
                            await websocket.send(dumps({
                                'authenticated': authenticated
                            }))
                    else:
                        await websocket.send(dumps({
                            'authenticated': authenticated
                        }))

    finally:
        pass


async def node_client(websocket, path):
    global nodes
    # Register.
    client = Node(websocket)
    try:
        # Implement logic here.
        authenticated = False
        while True:
            request = await websocket.recv()
            request = loads(request)
            #print("Node: {}".format(request))

            if authenticated:
                if request.get('request', None) == 'merge_corporations':
                    acquirer_id = request.get('acquirer_id', '')
                    acquiree_id = request.get('acquiree_id', '')
                    if acquiree_id != '' and acquirer_id != '':
                        # Transferring Inventories
                        corporations[acquirer_id].apply_inventory_delta_multiple(
                            corporations[acquiree_id].assets['inventory'])
                        # Changing acquiree's player's corp
                        for member in corporations[acquiree_id].members:
                            member.assign_corp(corporations[acquirer_id])
                        corporations[acquirer_id].gain_ore(corporations[acquiree_id].amount_of_ore())
                        corporations[acquiree_id].members = []
                        corporations.pop(acquiree_id, None)
                        # Server telling all child nodes to transfer corp belongings including players
                        # Transferring ownership of buildings is handled by the message
                        for node_name in nodes:
                            await nodes[node_name].connection.send(dumps({
                                'request': 'transfer_assets',
                                'key': config.keys['master'],
                                'acquirer_id': acquirer_id,
                                'acquiree_id': acquiree_id
                            }))
                elif request.get('request', None) == 'update_values':
                    #print("Updating values")
                    """
                    example_data = {
                        'corporations': {
                            '2dbb7bed-f20a-4e59-ac71-ab1ed87c89f7': {
                                'inventory_deltas': {
                                    'AttackPowerPotion': 0,
                                    'HealthPotion': 0,
                                    'HealthCapPotion': 0,
                                    'MinerMultiplierPotion': 0
                                },
                                'ore_delta': 3.0
                            }
                        }
                    }
                    """
                    data = request.get('data', None)
                    if data is not None:
                        for corp_id in data.get('corporations', {}):
                            if corp_id in corporations:
                                corp_obj = corporations[corp_id]
                                corp_obj.apply_child_server_deltas(data['corporations'][corp_id])
                    response = {
                        'corporations': {}
                    }
                    for corp_id in corporations:
                        corp_obj = corporations[corp_id]
                        response['corporations'][corp_id] = {
                            'ore_quantity': corp_obj.amount_of_ore(),
                            'inventory': corp_obj.assets['inventory']
                        }
                    #print(response)
                    await websocket.send(dumps({
                        'data': response,
                        'request': 'update_values'
                    }))

            else:
                if request.get('request', None) == 'register':
                    if request.get('name', None) is not None and request.get('public_address', None) is not None:
                        client.set_name(request.get('name', ''))
                        client.set_public_address(request.get('public_address', ''))
                        nodes[request.get('name', '')] = client
                        authenticated = True
                    await websocket.send(dumps({
                        'authenticated': authenticated
                    }))
                else:
                    await websocket.send(dumps({
                        'authenticated': authenticated,
                    }))
    finally:
        # Unregister.
        nodes.pop(client.name, None)
        print("Removed {} from pool of nodes".format(client.name))


start_node_server = websockets.serve(node_client, 'localhost', node_port)
start_player_server = websockets.serve(player, 'localhost', 7200)

asyncio.get_event_loop().run_until_complete(start_node_server)
asyncio.get_event_loop().run_until_complete(start_player_server)
asyncio.get_event_loop().run_forever()
