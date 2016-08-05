from flask import Flask, request, jsonify, url_for, render_template, make_response, redirect, current_app
import database_functions_

app = Flask(__name__)


def home_cor(obj):
    return_response = make_response(obj)
    return_response.headers['Access-Control-Allow-Origin'] = "*"
    return_response.headers['Access-Control-Allow-Methods'] = 'POST,GET,OPTIONS,PUT,DELETE'
    return_response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Origin, Accept"
    return return_response


@app.route('/account/create', methods=['POST'])
def account_create():
    pass


@app.route('/account/login', methods=['POST'])
def account_login():
    pass


@app.route('/game/join', methods=['POST'])
def game_join():
    pass


@app.route('/game/rejoin', methods=['POST'])
def game_rejoin():
    pass

app.run(debug=True, host='0.0.0.0', port=7004)
