from flask import Flask, request, jsonify, url_for, render_template, make_response, redirect, current_app
import database_functions_

app = Flask(__name__)


def home_cor(obj):
    return_response = make_response(obj)
    return_response.headers['Access-Control-Allow-Origin'] = "*"
    return_response.headers['Access-Control-Allow-Methods'] = 'POST,GET,OPTIONS,PUT,DELETE'
    return_response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Origin, Accept"
    return return_response


@app.route('/account/create', methods=['POST', 'OPTIONS'])
def account_create():
    data = request.json
    response = dict()
    if data is not None:
        username = data.get('username', None)
        password = data.get('password', None)
        if username is not None and password is not None:
            db_response = database_functions_.create_user(username, password)
            if db_response[0]:
                response['status'] = 'Success'
                response['uid'] = db_response[1]
            else:
                response['status'] = 'Error'
                response['error_message'] = db_response[1]
        else:
            response['status'] = 'Error'
            response['error_message'] = 'Username or Password are None'
    return home_cor(jsonify(**response))


@app.route('/account/login', methods=['POST'])
def account_login():
    data = request.json
    response = dict()
    if data is not None:
        username = data.get('username', None)
        password = data.get('password', None)
        if username is not None and password is not None:
            db_response = database_functions_.login(username, password)
            if db_response[0]:
                response['status'] = 'Success'
                response['uid'] = db_response[1]
            else:
                response['status'] = 'Error'
                response['error_message'] = db_response[1]
        else:
            response['status'] = 'Error'
            response['error_message'] = 'Username or Password are None'
    return home_cor(jsonify(**response))


@app.route('/game/join', methods=['POST'])
def game_join():
    pass


@app.route('/game/rejoin', methods=['POST'])
def game_rejoin():
    pass

app.run(debug=True, host='0.0.0.0', port=7004)
