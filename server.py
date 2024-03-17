import os
import psycopg2
import psycopg2.extras
import json
import jwt
import datetime
from functools import wraps
from applog import log
from hashlib import sha256
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from consumption import Energy, Water, Gas, Consumption, Resource
from tokens import TokenDto

app = Flask(__name__)

CWD = os.path.dirname(__file__)
credentials = json.load(open(os.path.join(CWD, "creds.json"), "r"))
DB_CONNECTION_STRING = "host=%s dbname=%s user=%s password=%s" % (credentials["DB_HOST"], credentials["DB_DATABASE"], credentials["DB_USER"], credentials["DB_PASSWORD"])

water = Water()
energy = Energy()
gas = Gas()

# Sample data for resources
resources = {
    "water": water,
    "energy": energy,
    "gas": gas
}

def query(cursor, string, data = ()):
    res = []
    cursor.execute(string, data)
    try:
        for row in cursor:
            res.append(row)
    except Exception as e:
        pass

    return res

def hash_password(username, password):
    return str(sha256((password + credentials["APPKEY"] + username).encode("UTF-8")).hexdigest())

def user_exists(username):
    dbConn = psycopg2.connect(DB_CONNECTION_STRING)
    cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    res = query(cursor, 'SELECT * FROM users WHERE name=(%s)', (username,))

    dbConn.commit()
    cursor.close()
    dbConn.close()

    return res != []

def token_required(f):
    @wraps(f)
    def token_dec(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return "Missing Token!", 400
        try:
            data = jwt.decode(token, credentials['APPKEY'], algorithms=["HS256"])
        except:
            return "Invalid Token", 400
        
        username = data["user"]
        if not user_exists(username):
            return "Invalid Token", 400

        return f(id=username, *args, **kwargs)
    return token_dec

@app.route('/areas/<area_name>', methods=['POST'])
@token_required
def manage_areas(area_name):
    if request.method == 'POST':
        dbConn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if area_name is None:
            return "Invalid area name", 400

        try:
            cons = Consumption(area=area_name)
            query(cursor, 'INSERT INTO areas (name, ) VALUES (%s)', area_name)
        except psycopg2.errors.UniqueViolation as e:
            return "Area '%s' already exists" % area_name, 400

        dbConn.commit()
        cursor.close()
        dbConn.close()
        return "Ok", 200


@app.route('/consumptions/<consumption_area>/', methods=['GET'])
@token_required
def get_consumption(consumption_area):
    if consumption_area not in resources:
        return jsonify({"error": "Invalid resource type"}), 400

    if request.method == 'GET':
        return jsonify({"value": resources[consumption_area]})
    

@app.route('/consumptions/<consumption_area>/', methods=['POST'])
@token_required
def manage_resources(consumption_area):
    try:
        data = request.get_json()
        price_per_unit = data.get("price_per_unit")
        if not price_per_unit:
            return jsonify({"error": "Missing value in request body"}), 400
        resources[resource_type] = Resource(price_per_unit, resources[resource_type].get_unit_type())
        return jsonify({"message": "Resource updated successfully"}), 200
    
    except:
        return jsonify({"error": "Invalid request data"}), 400


@app.route('users/<username>', methods=['POST'])
def register_user(username):
    dbConn = psycopg2.connect(DB_CONNECTION_STRING)
    cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    password = request.form["pass"]

    if None in (username, password):
        return "invalid username or password", 400

    hashed = hash_password(username, password)

    try:
        query(cursor, 'INSERT INTO users (name, pass) VALUES (%s, %s)', (username, hashed))
    except psycopg2.errors.UniqueViolation as e:
        return "Username '%s' already exists" % username, 400

    dbConn.commit()
    cursor.close()
    dbConn.close()
    return "Ok", 200

@app.route('/users/<username>', methods=["DELETE"])
@token_required
def delete_user(username):
    dbConn = psycopg2.connect(DB_CONNECTION_STRING)
    cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if None in (username,):
        return "invalid username or password", 400

    try:
        query(cursor, 'DELETE FROM users WHERE NAME=(%s)', (username,))
    except:
        return "Username '%s' cannot be deleted" % username, 400

    dbConn.commit()
    cursor.close()
    dbConn.close()
    return "Ok", 200

@app.route('/login/', methods=['GET'])
def login():
    dbConn = psycopg2.connect(DB_CONNECTION_STRING)
    cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    userAuth = request.authorization

    try:
        res = query(cursor, 'SELECT pass FROM users WHERE name=(%s)', (userAuth.username,))[0][0]
    except Exception as e:
        log(e)
        return "Invalid credentials", 400

    cursor.close()
    dbConn.close()

    hashed = hash_password(userAuth.username, userAuth.password)

    if userAuth and res == hashed:
        exp = datetime.datetime.now(datetime.utc()) + datetime.timedelta(hours=12)
        token = jwt.encode({'user' : userAuth.username, 'exp' : exp}, credentials['APPKEY'], algorithm="HS256")
        return TokenDto(token, exp).to_json(), 200
    return "Invalid credentials", 400


@app.route('/calendar/', methods=['GET', 'POST', 'DELETE'])
@token_required
def manage_calendar():

    if request.method == 'POST':
        dbConn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        title = request.form["title"]
        date = request.form["date"]
        description = request.form["description"]
        #warning = request.form["warning"]
        
        try:
            query(cursor, "INSERT INTO calendar VALUES (%s, %s, %s)", (title, date, description))
        except psycopg2.errors.UniqueViolation as e:
            return "Event already exists"

        dbConn.commit()
        cursor.close()
        dbConn.close()
        return jsonify({"message": "No calendar events yet."})
    elif request.method == 'GET':
        dbConn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        title = request.form["title"]
        date = request.form["date"]
        description = request.form["description"]
        
        # next YYYY-MM-DD
        next_date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
      
        event = query(cursor, "SELECT * FROM calendar WHERE date > %s AND date < %s description = %s", (title, date, next_date, description))
        
        if event:
            dbConn.commit()
            cursor.close()
            dbConn.close()
            return jsonify(event), 200
        else:
            dbConn.commit()
            cursor.close()
            dbConn.close()
            return jsonify({'message': 'Event not found'}), 200
    
    elif request.method == 'DELETE':
        dbConn = psycopg2.connect(DB_CONNECTION_STRING)
        cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        title = request.form["title"]
        date = request.form["date"]
        try:
            query(cursor, "DELETE FROM calendar WHERE VALUES = (%s, %s)", (title, date))
            dbConn.commit()
            cursor.close()
            dbConn.close()
            return jsonify({'message': 'Event deleted successfully'}), 200
        except psycopg2.errors.DataError as e:
            return jsonify({'message': 'Event not found'}), 404
    
    return jsonify({"error": "Method not implemented"}), 501

if __name__ == '__main__':
  app.run(threaded=True, debug=True)