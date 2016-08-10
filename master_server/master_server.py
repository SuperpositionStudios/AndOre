# This is the master server for the game.
# This server stores players (not the playercharacter), corporations, and links node servers.
# If this server goes down, players will still be able to do everything not related to corporations.

from flask import Flask, request, jsonify, url_for, render_template, make_response, redirect, current_app
import master_server_config as config
import requests
from master_game import player, corporation

app = Flask(__name__)


web_server_domain = "*"
nodes = {
    'master': {
        'name': 'master',
        'address': config.address
    },
    'nodes': dict()
}

corporations = []
players = dict()

def drint(text):
    if config.developing:
        print(text)


def home_cor(obj):
    return_response = make_response(obj)
    return_response.headers['Access-Control-Allow-Origin'] = web_server_domain
    return_response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Origin"
    return return_response


def is_valid_id(id):
    return id in players


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


def spawn_player(uid):
    player_obj = players[uid]
    player_node = players[uid].node
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
        drint("Successfully transferred new player to Cistuvaert")
    else:
        drint("Error while transferring new player to Cistuvaert")


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


@app.route('/valid_id', methods=['POST', 'OPTIONS'])
def valid_id():
    data = request.json
    response = dict()
    response['status'] = 'invalid'
    if data is not None:
        game_id = data.get('game_id', None)
        if game_id is not None:
            if is_valid_id(game_id):
                response['status'] = 'valid'
    return home_cor(jsonify(**response))


@app.route('/join')
def new_player():
    response = dict()

    new_corp = corporation.Corporation()
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
        response['world'] = {
            'name': player_node,
            'server': nodes['nodes'][player_node]['address']
        }
        response['status'] = 'Success'
    return home_cor(jsonify(**response))

app.run(debug=True, host='0.0.0.0', port=7100)
