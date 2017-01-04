# Nickname: Cynosural
from flask import Flask, request, jsonify, make_response, abort, Response, render_template
import os
import json
import util


def path_to_this_files_directory():
	dir_path = os.path.dirname(os.path.realpath(__file__))
	return dir_path + '/'


# Generate whitelisted_words set
with open(path_to_this_files_directory() + 'settings.json') as json_data:
	d = json.load(json_data)
in_production = d.get('inProduction', False)
url_key = "production" if in_production else "development"
urls = d.get('urls', None)

app = Flask(__name__)


def home_cor(obj):
	return_response = make_response(obj)
	return_response.headers['Access-Control-Allow-Origin'] = "*"
	return_response.headers['Access-Control-Allow-Methods'] = 'POST,GET,OPTIONS,PUT,DELETE'
	return_response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Origin, Accept"
	return return_response


@app.route('/')
def index():
	return render_template("main/index.html")


@app.route('/auth/login')
def auth_login():
	return render_template("auth/login.html")


@app.route('/auth/register')
def auth_register():
	return render_template("auth/register.html")


@app.route('/auth/logout')
def auth_logout():
	return render_template("auth/logout.html")


@app.route('/admin')
def admin():
	return render_template("admin/index.html")


@app.route('/gameclient')
def gameclient():
	return render_template("gameClient/index.html")


@app.route('/bengal')
def bengal():
	return render_template("Bengal/index.html")


@app.route('/wiki')
def wiki():
	return render_template("wiki/index.html")


@app.route('/sphere')
def sphere():
	return render_template("sphere/panel.html")


@app.route('/version', methods=['GET', 'OPTIONS'])
def version():
	if request.method == 'OPTIONS':
		return home_cor(jsonify(**{}))
	elif request.method == 'GET':
		return home_cor(jsonify(**{
			"git_version": util.get_git_revision_short_hash()
		}))


@app.route('/urls')
def get_urls():
	global urls
	response = {
		'erebus': urls['erebus'][url_key]
	}
	return home_cor(jsonify(**response))


app.run(debug=True, host='0.0.0.0', port=7002, threaded=True)
