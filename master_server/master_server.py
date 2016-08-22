# This is the master server for the game.
# This server stores players (not the playercharacter), corporations, and links node servers.
# If this server goes down, players will still be able to do everything not related to corporations.

from flask import Flask, request, jsonify, url_for, render_template, make_response, redirect, current_app
import master_server_config as config
import requests
from master_game import player, corporation
from master_game.player import Player
from master_game.corporation import Corporation
from typing import Dict

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

corporations = dict()  # type: Dict[str, Corporation]
players = dict()  # type: Dict[str, Player]


def drint(text):
    if config.developing:
        print(text)


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


def is_valid_node(node_name):
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


def message_all_nodes(endpoint, data, skip=None):
    for node_name in nodes['nodes']:
        if node_name == skip:
            continue
        req = requests.post(nodes['nodes'][node_name]['address'] + endpoint, json=data)
        node_response = req.json()
        if node_response['Successful_Request'] is False:
            print('Failed to update {node_name} with {data}'.format(node_name=node_name, data=str(data)))


def spawn_player(uid: str):
    player_obj = players[uid]
    player_node = players[uid].node
    # Checking that the player's node is valid
    if is_valid_node(player_node) is False:
        drint("Couldn't transfer new player to node {}".format(player_node))
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
        drint("Successfully transferred new player to {}".format(starter_system_name))
    else:
        drint("Error while transferring new player to {}".format(starter_system_name))


# This is the route that a node server goes to in order to establish a link.
# The process goes like this:
# node Server goes to this route and reveals their key
# Master Server checks if the key is valid, and if so it is added to the node server list.
# Master Server sends the node server the contact info for other node servers and also sends it's key.
# node Server will now send requests to view Corporation related details, and to modify them.
# Master Server will handle non-world related things, like merging corporations.
# The client of a route will always send their key.
@app.route('/register/node', methods=['POST', 'OPTIONS'])
def register_server():
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
                    member.corp = corporations[acquirer]
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
                print(corp_obj.assets['inventory'])
    for corp_id in corporations:
        corp_obj = corporations[corp_id]
        response['corporations'][corp_id] = {
            'ore_quantity': corp_obj.amount_of_ore(),
            'inventory': corp_obj.assets['inventory']
        }
    #drint(response)
    return home_cor(jsonify(**response))


@app.route('/valid_id', methods=['POST', 'OPTIONS'])
def valid_id():
    data = request.json
    response = dict()
    response['status'] = 'invalid'
    if data is not None:
        drint("/valid_id data is not none")
        game_id = data.get('game_id', None)
        if game_id is not None:
            drint("/valid_id game id is not none")
            if is_valid_id(game_id, verbose=True):
                drint("/valid_id id is valid")
                response['status'] = 'valid'
    return home_cor(jsonify(**response))


@app.route('/join')
def new_player():
    response = dict()

    new_corp = corporation.Corporation()
    new_corp.gain_ore(5000)
    corporations[new_corp.corp_id] = new_corp
    new_player_obj = player.Player(new_corp)
    players[new_player_obj.uid] = new_player_obj
    spawn_player(new_player_obj.uid)
    response['id'] = new_player_obj.uid

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


@app.route('/info')
def info():
    response = {
        'corporations': []
    }
    for c_id, _corporation in corporations.items():
        corp_info = {
            'id': _corporation.corp_id,
            'assets': _corporation.assets,
            'members': []
        }
        for member in _corporation.members:
            corp_info['members'].append({
                'id': member.uid,
                'node': member.node
            })
        response['corporations'].append(corp_info)
    return home_cor(jsonify(**response))


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
    return home_cor(jsonify(**response))

app.run(debug=True, host='0.0.0.0', port=7100, threaded=True)
