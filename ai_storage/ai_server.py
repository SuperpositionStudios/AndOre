from flask import Flask, request, jsonify, url_for, render_template, make_response, redirect, current_app
import database_functions

app = Flask(__name__)


def home_cor(obj):
    return_response = make_response(obj)
    return_response.headers['Access-Control-Allow-Origin'] = "*"
    return_response.headers['Access-Control-Allow-Methods'] = 'POST,GET,OPTIONS,PUT,DELETE'
    return_response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Origin, Accept"
    return return_response


@app.route('/retrieve', methods=['GET', 'POST', 'OPTIONS'])
def retrieve():
    data = request.json
    response = dict()
    if data is not None:
        print("Not none")
        mid = data.get('mid', '')
        response['model'] = database_functions.retrieve_model(mid)
    return home_cor(jsonify(**response))


@app.route('/upload', methods=['GET', 'POST', 'OPTIONS'])
def upload():
    data = request.json
    response = dict()
    if data is not None:
        print("Not none")
        mid = data.get('mid', '')
        model = data.get('model', '')
        response['model'] = database_functions.save_model(mid, model)
    return home_cor(jsonify(**response))

app.run(debug=True, host='0.0.0.0', port=7003)