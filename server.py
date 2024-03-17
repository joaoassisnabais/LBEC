import os
import jwt
import sqlite3
from functools import wraps
from urllib.parse import parse_qs
from hashlib import sha256
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify
from consumption import Energy, Water, Gas, Consumption, Resource
from tokens import TokenDto

app = Flask(__name__)

DATABASENAME = os.path.dirname(os.path.realpath(__file__)) + "/database.db"

def query(cursor, string, data = ()):
    res = []

    string = string % data
    
    cursor.execute(string)
    
    try:
        for row in cursor:
            res.append(row)
    except Exception as e:
        pass

    return res

def hash_password(username, password):
    return str(sha256((password + "random_string" + username).encode("UTF-8")).hexdigest())

def user_exists(username):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()

    res = query(cursor, 'SELECT * FROM users WHERE name=(%s)', (username,))

    conn.commit()
    cursor.close()
    conn.close()

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

@app.route('/consumptions/<area_name>', methods=['POST'])
@token_required
def post_areas(id, area_name):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()

    if area_name is None:
        return "Invalid area name", 400

    try:
        cons = Consumption(area=area_name)
        query(cursor, 'INSERT INTO consumptions (username, area_name, at_home, energy, water, gas) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\')',
                (id, cons.area, cons.at_home, cons.energy.amount, cons.water.amount, cons.gas.amount))
    
    except Exception as e:
        return "Area '%s' already exists" % area_name, 400

    conn.commit()
    conn.close()
    return "Ok", 200

@app.route('/consumptions/<area_name>/', methods=['GET'])  
@token_required
def get_consumption(id, area_name):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()

    if area_name is None:
        return "Invalid area name", 400

    try:
        cons = Consumption(area=area_name)
        req_time = request.args.get('requested_time')
        res = query(cursor, 'SELECT * FROM consumptions WHERE USERNAME=(\'%s\') AND AREA_NAME=(\'%s\') AND timestamp <= %s ORDER BY timestamp DESC LIMIT 1',
                    (id, cons.area, req_time))
    except Exception as e:
        return "Area '%s' already exists" % area_name, 400

    conn.commit()
    conn.close()
    return str(res), 200

@app.route('/users/<username>', methods=['POST'])   #DONE-TESTED
def register_user(username):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()

    request_data = parse_qs(request.get_data().decode('utf-8'))
    password = request_data.get('pass', [])
    password = password[0]

    if None in (username, password):
        return "invalid username or password", 400

    hashed = hash_password(username, password)

    try:
        query(cursor, 'INSERT INTO users (username, pass) VALUES (\'%s\', \'%s\')', (username, hashed))
    except Exception as e:
        return "Username '%s' already exists" % username, 400

    conn.commit()
    cursor.close()
    conn.close()
    return "Ok", 200

@app.route('/users/<username>', methods=["DELETE"])
@token_required
def delete_user(id):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()

    if id is None:
        return "Invalid username", 400

    try:
        query(cursor, 'DELETE FROM users WHERE USERNAME=(\'%s\')', (id))
    except:
        return "Username '%s' cannot be deleted" % id, 400

    conn.commit()
    cursor.close()
    conn.close()
    return "Ok", 200

@app.route('/login/', methods=['GET'])  #DONE-TESTED
def login():
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()
    
    request_data = parse_qs(request.get_data().decode('utf-8'))
    password = request_data.get('pass', [])[0]
    username = request_data.get('username', [])[0]

    try:
        res = query(cursor, 'SELECT pass FROM users WHERE username=(\'%s\')', (username))[0][0]
    except Exception as e:
        return "Invalid credentials", 400

    cursor.close()
    conn.close()

    hashed = hash_password(username, password)

    if res == hashed:
        exp = datetime.now(timezone.utc) + timedelta(hours=12)
        token = jwt.encode({'user' : username, 'exp' : exp}, "random_string", algorithm="HS256")
        return TokenDto(token, exp).to_json(), 200
    return "Invalid credentials", 400

@app.route('/calendar/', methods=['GET', 'POST', 'DELETE'])
@token_required
def manage_calendar(id):

    if request.method == 'POST':
        conn = sqlite3.connect(DATABASENAME)
        cursor = conn.cursor()
        
        title = request.form["title"]
        date = request.form["date"]
        description = request.form["description"]
        #warning = request.form["warning"]
        
        try:
            query(cursor, "INSERT INTO calendar (username, date, title, description) VALUES (\'%s\', \'%s\', \'%s\', \'%s\')", (id, date, title, description))
        except Exception as e:
            return "Event already exists", 400

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "No calendar events yet."})
    
    elif request.method == 'GET':
        conn = sqlite3.connect(DATABASENAME)
        cursor = conn.cursor(cursor_factory=sqlite3.extras.DictCursor)
        date = request.args.get('date')
        
        # next YYYY-MM-DD
        next_date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
      
        event = query(cursor, "SELECT * FROM calendar WHERE date > %s AND date < %s AND username = (\'%s\')", (date, next_date, id))
        
        if event:
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify(event), 200
        else:
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Event not found'}), 200
    
    elif request.method == 'DELETE':
        conn = sqlite3.connect(DATABASENAME)
        cursor = conn.cursor()
        
        title = request.form["title"]

        try:
            query(cursor, "DELETE FROM calendar WHERE title = (\'%s\') AND username = (\'%s\')", (title, id))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Event deleted successfully'}), 200
        except Exception as e:
            return jsonify({'message': 'Event not found'}), 404
    
    return jsonify({"error": "Method not implemented"}), 501

if __name__ == '__main__':
    SCHEMANAME = os.path.dirname(os.path.realpath(__file__)) + "/schema.sql"
    
    if not os.path.exists(DATABASENAME):
            connection = sqlite3.connect(DATABASENAME)

            with open(SCHEMANAME, "r") as f:
                connection.executescript(f.read())

            connection.commit()
            connection.close()
            
    app.run(debug=True)