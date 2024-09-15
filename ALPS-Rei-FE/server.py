import datetime
import os
from flask import *
app = Flask(__name__)

@app.route("/")
def root():
    return "ALPS-Rei-FE Web API"

@app.route("/clock")
def date_time():
    timezone = datetime.timezone(datetime.timedelta(hours = 9), "JST")
    now = datetime.datetime.now(timezone)
    return jsonify({"clock": now.strftime("%Y/%m/%d %H:%M:%S")})

@app.route("/receipt")
def receipt():
    if os.path.isfile("./receipt.json"):
        with open("./receipt.json", encoding = "utf-8") as f:
            return json.load(f)
    else:
        return jsonify({})

@app.route("/display")
def display():
    if os.path.isfile("./display.json"):
        with open("./display.json", encoding = "utf-8") as f:
            return json.load(f)
    else:
        return jsonify({})

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 5000)
