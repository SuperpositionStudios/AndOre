from flask import Flask, request, jsonify, url_for, render_template, make_response, redirect, current_app
import uuid, random
app = Flask(__name__)

web_server_domain = "*"
world_size = (32, 32)


def home_cor(obj):
    return_response = make_response(obj)
    return_response.headers['Access-Control-Allow-Origin'] = web_server_domain
    return_response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Origin"
    return return_response


def generate_starting_x_position():
    return random.randint(0, world_size[0])


def generate_starting_y_position():
    return random.randint(0, world_size[1])


class Player:

    def __init__(self, id):
        self._id = id
        self._health = 100
        self._ore_quantity = 0
        self._x_position = generate_starting_x_position()
        self._y_position = generate_starting_y_position()

    def input(self, dir):
        return ""

    def world_state(self):
        return ""



players = dict()


@app.route('/join')
def join():
    response = dict()
    new_id = str(uuid.uuid4())
    new_player = Player(id)
    players[new_id] = new_player
    response['id'] = new_id

    return home_cor(jsonify(**response))


@app.route('/action')
def action():
    response = dict()

    _id = request.args.get('id', '')
    if _id == '':
        response["error"] = "Error, too lazy to include what the error is"
        return home_cor(jsonify(**response))

    _act = request.args.get('act', '')
    players[_id].input(_act)

    _sendState = request.args.get('sendState', 'false')
    if _sendState == 'true':
        response['world'] = players[_id].world_state()
    return home_cor(jsonify(**response))


@app.route('/sendState')
def send_state():
    response = dict()

    _id = request.args.get('id', '')
    if _id == '':
        response['error'] = "Error, too lazy to include what the error is"
        return home_cor(jsonify(**response))

    response = dict()
    response['world'] = players[_id].world_state()
    return home_cor(jsonify(**response))


app.run(debug=True, host='0.0.0.0', port=7001)