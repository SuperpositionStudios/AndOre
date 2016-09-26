# Nickname: Andromeda

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")

app.run(debug=True, host='0.0.0.0', port=7002, threaded=True)
