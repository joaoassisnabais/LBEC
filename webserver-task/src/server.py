#!/bin/env python3

from flask import Flask, request
from data import Info, InfosDto, Repository, InfoRepoLocal, InfoRepoDatabase

app = Flask(__name__)

info_repository: Repository = InfoRepoDatabase()

# Routing...

@app.route("/put_data", methods=["POST", "GET"])
def put_data():
    latitude = request.values.get("Latitude", type=int)
    longitude = request.values.get("Longitude", type=int)
    speed = request.values.get("Speed", type=int)
    time = request.values.get("Time", type=str)

    if None in (latitude, longitude, speed, time):
        return "Missing field(s)!\n", 400
    
    info_repository.add(Info(latitude, longitude, speed, time))
    return "OK\n", 200


@app.route("/get_data", methods=["GET"])
def get_data():
    return InfosDto(info_repository.getAll()).to_json(), 200

if __name__ == "__main__":
    app.run(threaded=True)
