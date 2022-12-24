from flask import Flask, render_template

import stockviewer.db as db


app = Flask(__name__)


@app.route("/")
def index():
    db.sample_db_controll()
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9738, debug=True)
