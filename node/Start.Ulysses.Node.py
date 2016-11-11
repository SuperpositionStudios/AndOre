import config
from ws_node import Node
import websockets
import asyncio
import os
import json


def path_to_this_files_directory():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return dir_path + '/'

with open(path_to_this_files_directory() + 'settings.json') as json_data:
    d = json.load(json_data)

in_production = d.get('inProduction', False)

# Config

node_name = 'Ulysses'
node_port = 7102
production_public_address = 'ws://ulysses.iwanttorule.space'
development_public_address = 'ws://localhost:7102'

#

node_public_address = production_public_address if in_production else development_public_address

erebus_address = d.get('productionErebusAddress', '') if in_production else d.get('developmentErebusAddress', '')
sleipnir_address = d.get('productionSleipnirAddress', '') if in_production else d.get('developmentSleipnirAddress', '')

node_public_semi_address = 'localhost'

n = Node(node_name, node_port, node_public_address, erebus_address, sleipnir_address)

start_server = websockets.serve(n.game_client, node_public_semi_address, node_port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_until_complete(n.sleipnir_client())
asyncio.get_event_loop().run_forever()
