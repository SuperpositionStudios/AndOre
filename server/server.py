from flask import Flask, request, jsonify, url_for, render_template, make_response, redirect, current_app
import uuid, random
from player import Player
from cell import Cell
from world import World
from gameObject import GameObject, OreDeposit
import datetime
import os
import sys
import psutil
import logging
import warnings

app = Flask(__name__)

web_server_domain = "*"


world = World()
world.spawn_ore_deposits(20)
#world.spawn_hospitals(20)


def restart_program():
    """Restarts the current program, with file objects and descriptors
       cleanup
    """

    try:
        p = psutil.Process(os.getpid())
        for handler in p.get_open_files() + p.connections():
            os.close(handler.fd)
    except Exception as e:
        logging.error(e)

    python = sys.executable
    os.execl(python, python, *sys.argv)


def home_cor(obj):
    return_response = make_response(obj)
    return_response.headers['Access-Control-Allow-Origin'] = web_server_domain
    return_response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Origin"
    return return_response


def tick_server_if_needed():
    now = datetime.datetime.now()
    if (now - world.last_tick).microseconds >= world.microseconds_per_tick:
        world.tick()


@app.route('/join')
def join():
    assert(world)
    tick_server_if_needed()
    response = dict()

    new_player_id = world.new_player()

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
    if world.valid_player_id(_id) is False:
        response["error"] = "Invalid ID"
        return home_cor(jsonify(**response))

    _act = request.args.get('action', '')
    world.players[_id].action(_act)

    _sendState = request.args.get('sendState', 'false')

    if _sendState == 'true':
        return send_state(_id=_id)
    return home_cor(jsonify(**response))


@app.route('/sendState')
def send_state(**keyword_parameters):
    start_of_request = datetime.datetime.now()

    tick_server_if_needed()
    response = dict()

    if '_id' in keyword_parameters:
        _id = keyword_parameters['_id']
    else:
        _id = request.args.get('id', '')

    if world.valid_player_id(_id) is False:
        response['error'] = "Invalid ID"
        return home_cor(jsonify(**response))

    response = dict()
    response['world'] = world.players[_id].world_state()
    response['id'] = _id
    response['vitals'] = world.players[_id].get_vitals()

    request_time = datetime.datetime.now() - start_of_request
    print("Time to answer sendState request: {}".format(request_time.microseconds / 1000))
    return home_cor(jsonify(**response))


@app.route('/tick')
def run_ticks():
    world.world_age += 1
    response = dict()

    for player_id in world.players:
        world.players[player_id].tick()

    response['status'] = 'ticking'
    return home_cor(jsonify(**response))


@app.route('/restart')
def restart_route():
    restart_program()
    return "Restarted but since this restarted you won't be seeing this"

app.run(debug=True, host='0.0.0.0', port=7001, threaded=True)