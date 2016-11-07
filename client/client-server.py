# Nickname: Erebus

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("main/index.html")


@app.route('/admin')
def admin():
    return render_template("admin/index.html")


@app.route('/gameclient')
def gameclient():
    return render_template("gameClient/index.html")

app.run(debug=True, host='0.0.0.0', port=7002, threaded=True)
