# Nickname: Erebus

from flask import Flask, request, jsonify, url_for, render_template, make_response, redirect, current_app, abort, Response
import database_functions, requests, config, json

app = Flask(__name__)


def home_cor(obj):
    return_response = make_response(obj)
    return_response.headers['Access-Control-Allow-Origin'] = "*"
    return_response.headers['Access-Control-Allow-Methods'] = 'POST,GET,OPTIONS,PUT,DELETE'
    return_response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Origin, Accept"
    return return_response


@app.errorhandler(401)
def custom_401(error):
    return Response('Invalid Credentials', 401, {'Erebus':'error="Invalid Credentials"'})


@app.route('/account/create', methods=['POST', 'OPTIONS'])
def account_create():
    data = request.json
    response = dict()
    if request.method == 'OPTIONS':
        return home_cor(jsonify(**response))
    if data is not None:
        username = data.get('username', None)
        password = data.get('password', None)
        if username is not None and password is not None:
            db_response = database_functions.create_user(username, password)
            if db_response[0]:
                response['status'] = 'Success'
                response['uid'] = db_response[1]
                return home_cor(jsonify(**response))
    abort(401)


@app.route('/account/login', methods=['POST', 'OPTIONS'])
def account_login():
    data = request.json
    response = dict()
    if request.method == 'OPTIONS':
        return home_cor(jsonify(**response))
    if data is not None:
        username = data.get('username', None)
        password = data.get('password', None)
        if username is not None and password is not None:
            db_response = database_functions.login(username, password)
            if db_response[0]:
                response['status'] = 'Success'
                response['uid'] = db_response[1]
                return home_cor(jsonify(**response))
    abort(401)


@app.route('/game/join', methods=['POST', 'OPTIONS'])
def game_join():
    data = request.json
    response = dict()
    if data is not None:
        aid = data.get('uid', None)
        username = database_functions.get_username_from_aid(aid)
        if aid is not None and database_functions.valid_aid(aid) and username[0]:
            req = requests.post(config.game_server_url() + '/join', json={
                'aid': aid,
                'username': username[1]
            }).json()
            response['status'] = 'Success'
            response['game-id'] = req['id']
            gid = req['id']
            database_functions.update_game_id(aid, gid)
        else:
            response['status'] = 'Error'
            response['error_message'] = 'no uid was send in the request or invalid uid'
    else:
        response['status'] = 'Error'
        response['error_message'] = 'no json sent'
    return home_cor(jsonify(**response))


@app.route('/get/username', methods=['OPTIONS', 'GET'])
def get_username():
    if request.method == 'GET':
        response = {}
        aid = request.args.get('aid')
        username = database_functions.get_username_from_aid(aid)
        response['valid_aid'] = username[0]
        response['username'] = username[1]
        return home_cor(jsonify(**response))

    else:
        return home_cor(jsonify(**{}))


@app.route('/game/rejoin', methods=['POST', 'OPTIONS'])
def game_rejoin():
    data = request.json
    response = dict()
    if data is not None:
        aid = data.get('uid', None)
        username = database_functions.get_username_from_aid(aid)
        if aid is not None and database_functions.valid_aid(aid) and username[0]:
            response['status'] = 'Success'
            stored_game_id = database_functions.get_game_id(aid)[1]
            req = requests.post(config.game_server_url() + '/valid_id', json={
                'game_id': stored_game_id
            }).json()
            if req['status'] == 'valid':
                response['game-id'] = stored_game_id
            else:
                #req = requests.get(config_.game_server_url() + '/join')
                print(username)
                req = requests.post(config.game_server_url() + '/join', json={
                    'aid': aid,
                    'username': username[1]
                }).json()
                #game_server_response = req.json()
                new_game_id = req['id']
                database_functions.update_game_id(aid, new_game_id)
                response['game-id'] = req['id']
        else:
            response['status'] = 'Error'
            response['error_message'] = 'no uid was send in the request or invalid uid'
    else:
        response['status'] = 'Error'
        response['error_message'] = 'no json sent'
    return home_cor(jsonify(**response))


print("Starting Auth Server...")
print("Database file located at: {}".format(config.path_to_db()))
print("Master Server: {}".format(config.game_server_url()))

app.run(debug=True, host='0.0.0.0', port=7004)
