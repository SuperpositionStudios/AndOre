from flask import Flask, request, jsonify, url_for, render_template, make_response, redirect, current_app
import uuid, random
from player import Player
from cell import Cell
from world import World
from gameObject import GameObject, OreDeposit, EmptySpace

app = Flask(__name__)

web_server_domain = "*"


the_world = World()
#print(the_world.world[1][2].add_ore_deposit())
#print(the_world.world[0][0].obj_id)
#the_world.world[0][0].add_ore_deposit()
#the_world.world[0][0].remove_object(the_world.world[0][0].contains_object_type('OreDeposit')[1])
#print(the_world.world[0][1].obj_id)



def home_cor(obj):
    return_response = make_response(obj)
    return_response.headers['Access-Control-Allow-Origin'] = web_server_domain
    return_response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Origin"
    return return_response




def move_in_bounds(pos, axis):
    if axis == 'col':
        if pos < 0:
            return 0
        elif pos > world_size['col']:
            return world_size['col']
        else:
            return pos
    elif axis == 'row':
        if pos < 0:
            return 0
        elif pos > world_size['row']:
            return world_size['row']
        else:
            return pos

def valid_id(_id):
    if _id in player_ids:
        return True
    else:
        print("####")
        print("Invalid ID: " + _id)
        print(player_ids)
        print("####")
        return False


players = dict()
player_ids = []


@app.route('/join')
def join():
    assert(the_world)
    response = dict()
    new_id = str(uuid.uuid4())
    new_player = Player(new_id, the_world)
    player_ids.append(new_id)
    players[new_id] = new_player

    response['id'] = new_id

    _sendState = request.args.get('sendState', 'false')

    if _sendState == 'true':
        response['world'] = players[new_id].world_state()
        return send_state(_id=new_id)
    else:
        return home_cor(jsonify(**response))


@app.route('/action')
def action():
    response = dict()

    _id = request.args.get('id', '')
    if valid_id(_id) is False:
        response["error"] = "Invalid ID"
        return home_cor(jsonify(**response))

    _act = request.args.get('act', '')
    players[_id].input(_act)

    _sendState = request.args.get('sendState', 'false')
    if _sendState == 'true':
        response['world'] = players[_id].world_state()
    return home_cor(jsonify(**response))


@app.route('/sendState')
def send_state(**keyword_parameters):

    response = dict()

    if '_id' in keyword_parameters:
        _id = keyword_parameters['_id']
    else:
        _id = request.args.get('id', '')

    if valid_id(_id) is False:
        response['error'] = "Invalid ID"
        return home_cor(jsonify(**response))

    response = dict()
    response['world'] = players[_id].world_state()
    response['id'] = _id
    return home_cor(jsonify(**response))


app.run(debug=True, host='0.0.0.0', port=7001,threaded=True)