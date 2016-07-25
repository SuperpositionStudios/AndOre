from flask import Flask, request, jsonify, url_for, render_template, make_response, redirect, current_app
import uuid, random
from player import Player
from cell import Cell
from world import World
from gameObject import GameObject, OreDeposit
import datetime
app = Flask(__name__)

web_server_domain = "*"


world = World()
#world.world[4][4].add_ore_deposit()
world.spawn_ore_deposits(20)
world.spawn_hospitals(20)
#world.world[8][8].add_hospital()


def home_cor(obj):
    return_response = make_response(obj)
    return_response.headers['Access-Control-Allow-Origin'] = web_server_domain
    return_response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Origin"
    return return_response


def move_in_bounds(pos, axis):
    if axis == 'col':
        if pos < 0:
            return 0
        elif pos > world.cols:
            return world.cols
        else:
            return pos
    elif axis == 'row':
        if pos < 0:
            return 0
        elif pos > world.rows:
            return world.rows
        else:
            return pos


def valid_id(_id):
    if _id in player_ids:
        return True
    else:
        #print("####")
        #print("Invalid ID: " + _id)
        #print(player_ids)
        #print("####")
        return False


def tick_server_if_needed():
    now = datetime.datetime.now()
    if (now - world.last_tick).microseconds >= world.microseconds_per_tick:
        run_ticks()

player_ids = []


@app.route('/join')
def join():
    assert(world)
    tick_server_if_needed()
    response = dict()

    new_player_id = world.new_player()

    player_ids.append(new_player_id)
    response['id'] = new_player_id

    _sendState = request.args.get('sendState', 'false')

    if _sendState == 'true':
        response['world'] = world.players[new_player_id].world_state()
        return send_state(_id=new_player_id)
    else:
        return home_cor(jsonify(**response))


@app.route('/action')
def action():
    tick_server_if_needed()
    response = dict()

    _id = request.args.get('id', '')
    if valid_id(_id) is False:
        response["error"] = "Invalid ID"
        return home_cor(jsonify(**response))

    _act = request.args.get('action', '')
    world.players[_id].action(_act)

    _sendState = request.args.get('sendState', 'false')
    if _sendState == 'true':
        response['world'] = world.players[_id].world_state()
    return home_cor(jsonify(**response))


@app.route('/sendState')
def send_state(**keyword_parameters):
    tick_server_if_needed()
    response = dict()

    if '_id' in keyword_parameters:
        _id = keyword_parameters['_id']
    else:
        _id = request.args.get('id', '')

    if valid_id(_id) is False:
        response['error'] = "Invalid ID"
        return home_cor(jsonify(**response))

    response = dict()
    response['world'] = world.players[_id].world_state()
    response['id'] = _id
    response['vitals'] = world.players[_id].get_vitals()
    return home_cor(jsonify(**response))


@app.route('/tick')
def run_ticks():
    world.world_age += 1
    response = dict()

    for player_id in world.players:
        world.players[player_id].tick()

    response['status'] = 'ticking'
    return home_cor(jsonify(**response))

app.run(debug=True, host='0.0.0.0', port=7001, threaded=True)