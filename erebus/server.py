from flask import Flask, request, jsonify, make_response, abort, Response, url_for
import database_functions
import config
import erebus_util
import exceptions
import json

app = Flask(__name__)

public_address = json.load(open(erebus_util.path_to_this_files_directory() + 'settings.json')).get('public_address', '')


def home_cor(obj):
	return_response = make_response(obj)
	return_response.headers['Access-Control-Allow-Origin'] = "*"
	return_response.headers['Access-Control-Allow-Methods'] = 'POST,GET,OPTIONS,PUT,DELETE'
	return_response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Origin, Accept"
	return return_response


@app.errorhandler(401)
def http_401(message=''):
	if message == '':
		return home_cor(Response('Invalid Credentials', 401, {'Erebus': 'error="Invalid Credentials"'}))
	else:
		return home_cor(Response(message, 401))


@app.route('/', methods=['OPTIONS', 'GET'])
def root():
	if request.method == 'GET':
		response = {
			'endpoints': {
				'users': public_address + url_for('users', aid='aid_here'),
				'account': public_address + url_for('account')
			}
		}
		return home_cor(jsonify(**response))
	else:
		return home_cor(jsonify(**{}))


@app.route('/account', methods=['OPTIONS', 'GET'])
def account():
	if request.method == 'GET':
		response = {
			'endpoints': {
				'create': public_address + url_for('account_create'),
				'login': public_address + url_for('account_login')
			}
		}
		return home_cor(jsonify(**response))
	else:
		return home_cor(jsonify(**{}))


@app.route('/account/create', methods=['POST', 'OPTIONS', 'GET'])
def account_create():
	response = dict()

	if request.method == 'OPTIONS':
		return home_cor(jsonify(**response))
	elif request.method == 'GET':
		username = request.args.get('username', '')
		password = request.args.get('password', '')

		db_response = database_functions.create_user(username, password)

		if db_response[0]:
			response['status'] = 'Success'
			response['uid'] = db_response[1]
			return home_cor(jsonify(**response))
		else:
			return http_401('Username Taken.')
	elif request.method == 'POST':
		data = request.json
		if data is not None:
			username = data.get('username', None)
			password = data.get('password', None)
			if username is not None and password is not None:
				db_response = database_functions.create_user(username, password)
				if db_response[0]:
					response['status'] = 'Success'
					response['uid'] = db_response[1]
					return home_cor(jsonify(**response))
		return http_401()


@app.route('/account/login', methods=['POST', 'OPTIONS', 'GET'])
def account_login():
	response = dict()

	if request.method == 'OPTIONS':
		return home_cor(jsonify(**response))
	elif request.method == 'GET':
		username = request.args.get('username', '')
		password = request.args.get('password', '')
		aid = database_functions.login(username, password)
		response['valid_aid'] = aid[0]
		response['aid'] = aid[1]
		return home_cor(jsonify(**response))
	elif request.method == 'POST':
		data = request.json
		if data is not None:
			username = data.get('username', None)
			password = data.get('password', None)
			if username is not None and password is not None:
				db_response = database_functions.login(username, password)
				if db_response[0]:
					response['status'] = 'Success'
					response['uid'] = db_response[1]
					return home_cor(jsonify(**response))
		return http_401()


@app.route('/get/username', methods=['OPTIONS', 'GET'])
def get_username():
	if request.method == 'GET':
		response = {}
		aid = request.args.get('aid', '')
		if aid is not '':
			try:
				username = database_functions.get_username(aid)
			except exceptions.InvalidAid:
				response['valid_aid'] = False
			else:
				response['valid_aid'] = True
				response['username'] = username
			finally:
				return home_cor(jsonify(**response))
	else:
		return home_cor(jsonify(**{}))


@app.route('/users/<aid>', methods=['OPTIONS', 'GET'])
def users(aid: str):
	if request.method == 'GET':
		response = {
			'endpoints': {
				'username': public_address + url_for('users_username', aid=aid),
				'privileges': public_address + url_for('users_privileges', aid=aid),
				'last_login': public_address + url_for('users_last_login', aid=aid)
			}
		}
		return home_cor(jsonify(**response))
	else:
		return home_cor(jsonify(**{}))


@app.route('/users/<aid>/username', methods=['OPTIONS', 'GET'])
def users_username(aid: str):
	if request.method == 'GET':
		response = {}
		try:
			username = database_functions.get_username(aid)
		except exceptions.InvalidAid:
			response['valid_aid'] = False
		else:
			response['valid_aid'] = True
			response['username'] = username
		finally:
			return home_cor(jsonify(**response))
	else:
		return home_cor(jsonify(**{}))


@app.route('/users/<aid>/privileges', methods=['OPTIONS', 'GET'])
def users_privileges(aid: str):
	if request.method == 'GET':
		response = {}
		try:
			privileges = database_functions.get_privilege(aid)
		except exceptions.InvalidAid:
			response['valid_aid'] = False
		else:
			response['privileges'] = privileges
			response['valid_aid'] = True
		finally:
			return home_cor(jsonify(**response))
	else:
		return home_cor(jsonify(**{}))


@app.route('/users/<aid>/last_login', methods=['OPTIONS', 'GET'])
def users_last_login(aid: str):
	if request.method == 'GET':
		response = {}
		try:
			last_login = database_functions.get_last_login(aid)
		except exceptions.InvalidAid:
			response['valid_aid'] = False
		else:
			response['last_login'] = last_login
			response['valid_aid'] = True
		finally:
			return home_cor(jsonify(**response))
	else:
		return home_cor(jsonify(**{}))

print("Starting Erebus with Public Address: {}".format(public_address))
print("Database file located at: {}".format(config.path_to_db()))

app.run(debug=True, host='0.0.0.0', port=7004)
