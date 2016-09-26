# This is the master server for the game.
# It's nickname is Sleipnir.
# This server stores player data (but not player character), corporations, and links node servers.
# If this server goes down, all nodes are useless.

from flask import Flask, request, jsonify, make_response, redirect, current_app
import master_server_config as config
import requests
from typing import Dict, List
import game_classes

app = Flask(__name__)

starter_system_name = 'Panagoul'

web_server_domain = "*"
nodes = {
    'master': {
        'name': 'master',
        'address': config.address
    },
    'nodes': dict()
}

corporations = dict()  # type: Dict[str, game_classes.Corporation]
players = dict()  # type: Dict[str, game_classes.Player]
pending_requests = dict()  # type: Dict[str, List[Dict]]


def queue_request(node_name: str, req: Dict) -> bool:
    """
    :param node_name: The name of the node that the request is going to be sent to
    :param req: The dict object containing information about the request including it's request type
    :return: A boolean with whether the request was successfully queued
    """
    if node_name in pending_requests:
        pending_requests[node_name].append(req)
        return True
    return False


def reset_pending_requests():
    pending_requests = dict()


def home_cor(obj):
    return_response = make_response(obj)
    return_response.headers['Access-Control-Allow-Origin'] = web_server_domain
    return_response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Origin"
    return return_response


def is_valid_id(uid: str, verbose=False):
    if verbose:
        print("Trying to find {} in".format(uid))
        print(players)
    if uid in players:
        if verbose:
            print("valid id")
        return True
    else:
        if verbose:
            print("invalid id")
        return False


def is_valid_node(node_name: str) -> bool:
    return node_name in nodes['nodes']


def update_nodes_on_new_nodes(skip=None):
    for node_name in nodes['nodes']:
        if node_name == skip:
            continue
        req = requests.post(nodes['nodes'][node_name]['address'] + '/update/nodes', json={
            'key': config.keys['master'],
            'nodes': nodes
        })
        node_response = req.json()
        if node_response['Successful_Request'] is False:
            print('Failed to update {node_name} on new nodes'.format(node_name=node_name))


def message_node(endpoint: str, node_name: str, data: dict) -> dict:
    address = nodes['nodes'][node_name]['address'] + endpoint
    req = requests.post(address, json=data)
    response = req.json()
    if response is None:
        response = {}
    return response


def message_all_nodes(endpoint: str, data: dict, skip=None):
    for node_name in nodes['nodes']:
        if node_name == skip:
            continue
        node_response = message_node(endpoint, node_name, data)
        if node_response.get('Successful_Request', False) is False:
            print('Failed to update {node_name} with {data}'.format(node_name=node_name, data=str(data)))


def spawn_player(uid: str) -> None:
    player_obj = players[uid]
    player_node = players[uid].node
    # Checking that the player's node is valid
    if is_valid_node(player_node) is False:
        print("Couldn't transfer new player to node {} due to it not being valid.".format(player_node))
        return
    req = requests.post(nodes['nodes'][player_node]['address'] + '/player/enter', json={
        'player': {
            'uid': player_obj.uid,
            'corporation': {
                'corp_id': player_obj.corp.corp_id,
                'ore_quantity': player_obj.corp.amount_of_ore()
            }
        }
    })
    node_response = req.json()
    if node_response['Successful_Request']:
        print("Successfully transferred new player to ", starter_system_name)
    else:
        print("Error while transferring new player to ", starter_system_name)


@app.route('/register/node', methods=['POST', 'OPTIONS'])
def register_server():
    # This is the route that a node server goes to in order to establish a link.
    # The process goes like this:
    # node Server goes to this route and reveals their key
    # Master Server checks if the key is valid, and if so it is added to the node server list.
    # Master Server sends the node server the contact info for other node servers and also sends it's key.
    # node Server will now send requests to view Corporation related details, and to modify them.
    # Master Server will handle non-world related things, like merging corporations.
    # The client of a route will always send their key.
    response = dict()
    data = request.json
    node_key = data.get('key', None)
    node_name = data.get('name', None)
    node_address = data.get('address', None)
    # Checking that none of the required inputs are None
    if node_key is None or node_name is None or node_address is None:
        response['Successful_Request'] = False
        return home_cor(jsonify(**response))
    # Official Server Confirming
    if node_key != config.keys['node']:
        response['Successful_Request'] = False
        return home_cor(jsonify(**response))
    global nodes
    nodes['nodes'][node_name] = {
        'name': node_name,
        'address': node_address
    }
    response['Successful_Request'] = True
    response['nodes'] = nodes
    update_nodes_on_new_nodes(skip=node_name)
    return home_cor(jsonify(**response))


@app.route('/merge_corporations', methods=['POST', 'OPTIONS'])
def merge_corporations():
    response = {
        'Successful_Request': False
    }
    data = request.json
    if data is not None:
        node_key = data.get('key', None)
        acquirer = data.get('acquirer_id', None)
        acquiree = data.get('acquiree_id', None)
        if node_key is not None and acquirer is not None and acquiree is not None:
            if node_key == config.keys['node']:
                response['Successful_Request'] = True
                # Transferring Inventories
                corporations[acquirer].apply_inventory_delta_multiple(corporations[acquiree].assets['inventory'])
                # Changing acquiree's player's corp
                for member in corporations[acquiree].members:
                    member.assign_corp(corporations[acquirer])
                corporations[acquirer].gain_ore(corporations[acquiree].amount_of_ore())
                corporations[acquiree].members = []
                corporations.pop(acquiree, None)
                # Server telling all child nodes to transfer corp belongings including players
                # Transferring ownership of buildings is handled by the message
                message_all_nodes('/transfer_assets', {
                    'master_key': config.keys['master'],
                    'acquirer_id': acquirer,
                    'acquiree_id': acquiree
                })
    return jsonify(**response)


@app.route('/update_values', methods=['POST', 'OPTIONS'])
def update_values():
    # Route used for updating values stored here.
    # For now we'll use this to update corp ore quantities
    # and this will return the new quantities.
    data = request.json
    response = dict()
    response['Successful_Request'] = False
    response['corporations'] = dict()
    if data is not None:
        response['Successful_Request'] = True
        # TODO: Check if this request comes from a verified node
        for corp_id in data['corporations']:
            if corp_id in corporations:
                corp_obj = corporations[corp_id]
                corp_obj.apply_child_server_deltas(data['corporations'][corp_id])
    for corp_id in corporations:
        corp_obj = corporations[corp_id]
        response['corporations'][corp_id] = {
            'ore_quantity': corp_obj.amount_of_ore(),
            'inventory': corp_obj.assets['inventory']
        }
    return home_cor(jsonify(**response))


@app.route('/valid_id', methods=['POST', 'OPTIONS'])
def valid_id():
    data = request.json
    response = dict()
    response['status'] = 'invalid'
    if data is not None:
        game_id = data.get('game_id', None)
        if game_id is not None:
            if is_valid_id(game_id, verbose=True):
                response['status'] = 'valid'
    return home_cor(jsonify(**response))


@app.route('/join', methods=['POST', 'OPTIONS'])
def new_player():
    data = request.json
    response = dict()
    response['status'] = 'invalid'
    if data is not None:
        aid = data.get('aid', None)
        username = data.get('username', None)
        if aid is not None and username is not None:
            new_corp = game_classes.Corporation()
            new_corp.gain_ore(5000)
            corporations[new_corp.corp_id] = new_corp
            player = game_classes.Player()
            player.assign_corp(new_corp)
            player.assign_aid(aid)
            player.assign_username(username)
            players[player.uid] = player
            spawn_player(player.uid)
            response['id'] = player.uid
            response['status'] = 'valid'

    return home_cor(jsonify(**response))


@app.route('/get_player_info')
def get_player_info():
    player_id = request.args.get('id', '')
    response = {
        'status': 'Error'
    }
    if is_valid_id(player_id):
        player_node = players[player_id].node
        if is_valid_node(player_node):
            response['world'] = {
                'name': player_node,
                'server': nodes['nodes'][player_node]['address']
            }
            response['status'] = 'Success'
    return home_cor(jsonify(**response))


# TODO: Only enable this route when developing
@app.route('/info')
def info():
    # Creating the layout of the response
    response = {
        'servers': {
            'master': {
                'address': nodes['master']['address'],
                'name': 'master'
            },
            'nodes': []
        },
        'corporations': []
    }
    # Adding nodes & their options to the response
    for node_name, node in nodes['nodes'].items():
        evac_list = {}
        for key, val in nodes['nodes'].items():
            if key != node_name:
                evac_list[key] = nodes['master']['address'] + '/move_all_players_from/' + node_name + '/to/' + key
        response['servers']['nodes'].append({
            'name': node_name,
            'address': node['address'],
            'dev': {
                'evac': evac_list
            }
        })
    # Adding corporations to the response
    for c_id, _corporation in corporations.items():
        corp_info = {
            'id': _corporation.corp_id,
            'assets': _corporation.assets,
            'members': []
        }
        # Adding corp members to the response
        for member in _corporation.members:
            corp_info['members'].append({
                'debug': {
                    'sendState': nodes['nodes'][member.node]['address'] + '/sendState?id=' + member.uid,
                },
                'id': member.uid,
                'node': member.node,
                'aid': member.aid,
                'username': member.username
            })
        response['corporations'].append(corp_info)
    return home_cor(jsonify(**response))


# TODO: Only enable this route when developing
@app.route('/move_all_players_from/<system1>/to/<system2>')
def move_all_players_from(system1, system2):
    response = {
        'status': 'Error'
    }
    if is_valid_node(system1) and is_valid_node(system2):
        response['status'] = 'Success'
        for playerName, player in players.items():
            if player.node == system1:
                player.node = system2
                spawn_player(player.uid)
    return home_cor(jsonify(**response))


@app.route('/player/transfer_node', methods=['POST', 'OPTIONS'])
def route_player_transfer_origin_to():
    data = request.json
    response = dict()
    response['Successful_Request'] = False
    if data is not None:
        # TODO: Check if this request comes from a verified node
        gid = data.get('gid', '')  # type: str
        origin_node = data.get('origin', '')  # type: str
        destination_node = data.get('destination', '')  # type: str
        if is_valid_id(gid) and is_valid_node(origin_node) and is_valid_node(destination_node):
            # Tell the player's current node to remove them from the world and reply to any future requests
            # with a flag telling them to contact the master server for their new node
            message_node('/player/leave', origin_node, {
                'gid': gid
            })
            # Setting the player's new node
            if players.get(gid, None) is not None:
                players.get(gid).assign_node(destination_node)
            # Contacting the new node instructing it to spawn the player in it's world
            spawn_player(gid)
            response['Successful_Request'] = True

    return home_cor(jsonify(**response))


app.run(debug=True, host='0.0.0.0', port=7100, threaded=True)
