# Nickname: Cynosural
from flask import Flask, request, jsonify, make_response, abort, Response, render_template

app = Flask(__name__)


def home_cor(obj):
	return_response = make_response(obj)
	return_response.headers['Access-Control-Allow-Origin'] = "*"
	return_response.headers['Access-Control-Allow-Methods'] = 'POST,GET,OPTIONS,PUT,DELETE'
	return_response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Origin, Accept"
	return return_response


@app.route('/')
def index():
	return render_template("gameClient/index.html")


@app.route('/auth/login')
def auth_login():
	return render_template("auth/login.html")


@app.route('/auth/register')
def auth_register():
	return render_template("auth/register.html")


@app.route('/admin')
def admin():
	return render_template("admin/index.html")


@app.route('/gameclient')
def gameclient():
	return render_template("gameClient/index.html")


@app.route('/bengal')
def bengal():
	return render_template("Bengal/index.html")


@app.route('/urls')
def get_urls():
	urls = {
		'erebus': 'http://erebus.andore.online'
	}
	return home_cor(jsonify(**urls))


app.run(debug=True, host='0.0.0.0', port=7002, threaded=True)
