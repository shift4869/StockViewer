import asyncio
from flask import Flask, render_template

from StockLoader import StockLoader
from StockFetcher import StockFetcher
from StockSaver import StockSaver
import db as db


app = Flask(__name__)


@app.route("/")
def index():
    sl = StockLoader()
    records = sl.select_table()
    return render_template("index.html", table=records)


@app.route("/update/")
def update():
    sf = StockFetcher()
    content = None
    loop = asyncio.get_event_loop()
    content = loop.run_until_complete(sf.fetch())
    table_data = sf.parse_table(content)

    ss = StockSaver()
    ss.insert_table(table_data)
    return {"result": "OK"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9738, debug=True)
