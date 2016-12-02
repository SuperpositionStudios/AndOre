# Nickname: Erebus

from flask import Flask, request, jsonify, make_response, abort, Response
import database_functions, config, json

app = Flask(__name__)


def home_cor(obj):
	return_response = make_response(obj)
	return_response.headers['Access-Control-Allow-Origin'] = "*"
	return_response.headers['Access-Control-Allow-Methods'] = 'POST,GET,OPTIONS,PUT,DELETE'
	return_response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Origin, Accept"
	return return_response


@app.errorhandler(401)
def custom_401(error):
	return home_cor(Response('Invalid Credentials', 401, {'Erebus': 'error="Invalid Credentials"'}))


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


print("Starting Auth Server...")
print("Database file located at: {}".format(config.path_to_db()))

app.run(debug=True, host='0.0.0.0', port=7004)
