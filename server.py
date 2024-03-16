import os
import psycopg2
import psycopg2.extras
import json
import jwt
from functools import wraps
from applog import log
from hashlib import sha256
from flask import Flask, request, jsonify
from consumption import Energy, Water, Gas, Consumption, Resource
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

CWD = os.path.dirname(__file__)
credentials = json.load(open(os.path.join(CWD, "creds.json"), "r"))
DB_CONNECTION_STRING = "host=%s dbname=%s user=%s password=%s" % (credentials["DB_HOST"], credentials["DB_DATABASE"], credentials["DB_USER"], credentials["DB_PASSWORD"])


# In-memory user data (replace with database later)
users = {}


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

@app.route('/resources/<resource_type>/', methods=['GET', 'PUT'])
def manage_resources(resource_type):
    if resource_type not in resources:
        return jsonify({"error": "Invalid resource type"}), 400

    if request.method == 'GET':
        return jsonify({"value": resources[resource_type]})
    
    elif request.method == 'PUT':
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


@app.route('/login', methods=['GET'])
def login():
  # Implement header-based authentication logic here
  # This example requires a header named 'Authorization' with a Basic Auth token
  auth = request.headers.get('Authorization')
  if not auth or not auth.startswith('Basic '):
    return jsonify({"error": "Missing or invalid authorization header"}), 401

  # Extract username and password from the header
  username, password = auth.split()[1].decode('utf-8').split(':')
  if username not in users:
    return jsonify({"error": "Invalid username or password"}), 401

  # Check password against stored hash
  if not check_password_hash(users[username]["password"], password):
    return jsonify({"error": "Invalid username or password"}), 401

  # Login successful, return a success message (replace with token generation if needed)
  return jsonify({"message": "Login successful!"}), 200


@app.route('/calendar/', methods=['GET', 'POST'])
def manage_calendar():
  #TODO: Implement calendar management logic here
  # This is a basic example, replace with actual calendar functionality
  if request.method == 'POST':
        date = request.form["date"]
        name = request.form["name"]
        warning = request.form["warning"]
      
        return jsonify({"message": "No calendar events yet."})
  elif request.method == 'GET':
        # Implement logic to add/update calendar events based on request data
        return jsonify({"message": "Calendar event updated successfully"}), 200

  return jsonify({"error": "Method not implemented"}), 501


if __name__ == '__main__':
  app.run(threaded=True, debug=True)