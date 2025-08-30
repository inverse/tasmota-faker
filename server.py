import os

from flask import Flask, Response, request

from tasmota_faker import status_template

instance = os.getenv("INSTANCE", 1)

app = Flask(__name__)


@app.route("/")
def index():
    return "Welcome to Tasmota Faker!"


@app.route("/cm")
def cm():
    args = request.args

    cmnd = args.get("cmnd")

    if not cmnd:
        return Response("No command provided!", status=400)

    cmnd = cmnd.lower()

    if cmnd == "status 0":
        return status_template("sample", request.host.split(":")[0], instance)

    return Response(f"Command '{cmnd}' received!", status=501)
