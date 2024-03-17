import os
import jwt
import sqlite3
import time
import threading
from emails import Send_Email
from functools import wraps
from urllib.parse import parse_qs
from hashlib import sha256
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify
from consumption import Consumption
from tokens import TokenDto
from ideal import ideal_consumption
from EventCalendar import Calendar, Event

app = Flask(__name__)

DATABASENAME = os.path.dirname(os.path.realpath(__file__)) + "/database.db"

def parse_timestamp():
    try:
        request_data = parse_qs(request.get_data().decode('utf-8'))
        year = request_data.get('year', [])[0]
        month = request_data.get('month', [])[0]
        day = request_data.get('day', [])[0]
        hour = request_data.get('hours', [])[0]
        minute = 0
        second = 0
        req_time = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        return req_time
    except Exception as e:
        pass
    return None

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

    res = query(cursor, 'SELECT * FROM users WHERE username=(\'%s\')', (username))

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
            data = jwt.decode(token, "random_string", algorithms=["HS256"])
        except:
            return "Invalid Token", 400
        
        username = data["user"]
        if not user_exists(username):
            return "Invalid Token", 400

        return f(id=username, *args, **kwargs)
    return token_dec

@app.route('/consumptions/optimal', methods=['GET'])
@token_required
def get_optimal_consumption(id):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()
    
    request_data = parse_qs(request.get_data().decode('utf-8'))
    current_temp = request_data.get('current_temp', [])[0]
    not_at_home = request_data.get('not_at_home', [])[0]
    if not_at_home == 0:
        not_at_home = False
    else:
        not_at_home = True
    
    try:
        res = query(cursor, 'SELECT temp_max, temp_min FROM users WHERE username=(\'%s\')', (id))
        temp_max = res[0][0]
        temp_min = res[0][1]
        
    except Exception as e:
        return "User '%s' with difficulties" % id, 400
    
    return str(ideal_consumption(temp_min, temp_max, not_at_home, current_temp, 20))

@app.route('/consumptions/<area_name>/month', methods=['GET']) #DONE-TESTED
@token_required
def get_consumption_month(id, area_name):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()

    if area_name is None:
        return "Invalid area name", 400

    try:
        format="%F %T"
        req_time = parse_timestamp()
        next_month = req_time + timedelta(months=1)
        req_time = req_time.strftime(format)
        next_month = next_month.strftime(format)
        
        res = query(cursor, 'SELECT * FROM consumptions WHERE USERNAME=(\'%s\') AND AREA_NAME=(\'%s\') AND timestamp <= \'%s\' AND timestamp >= \'%s\' ORDER BY timestamp DESC LIMIT 24',
                    (id, area_name, next_month, req_time))
        
    except Exception as e:
        return "Area '%s' with difficulties" % area_name, 400

    conn.commit()
    conn.close()
    
    total_energy = sum([row[4] for row in res])
    total_water = sum([row[5] for row in res])
    total_gas = sum([row[6] for row in res])

    result = {
        "total_energy": total_energy,
        "total_water": total_water,
        "total_gas": total_gas
    }

    return jsonify(result), 200

@app.route('/consumptions/<area_name>/week', methods=['GET']) #DONE-TESTED
@token_required
def get_consumption_week(id, area_name):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()

    if area_name is None:
        return "Invalid area name", 400

    try:
        format="%F %T"
        req_time = parse_timestamp()
        next_week = req_time + timedelta(days=7)
        req_time = req_time.strftime(format)
        next_day = next_week.strftime(format)
        
        res = query(cursor, 'SELECT * FROM consumptions WHERE USERNAME=(\'%s\') AND AREA_NAME=(\'%s\') AND timestamp <= \'%s\' AND timestamp >= \'%s\' ORDER BY timestamp DESC LIMIT 24',
                    (id, area_name, next_week, req_time))
        
    except Exception as e:
        return "Area '%s' with difficulties" % area_name, 400

    conn.commit()
    conn.close()
    
    total_energy = sum([row[4] for row in res])
    total_water = sum([row[5] for row in res])
    total_gas = sum([row[6] for row in res])

    result = {
        "total_energy": total_energy,
        "total_water": total_water,
        "total_gas": total_gas
    }

    return jsonify(result), 200

@app.route('/consumptions/<area_name>/day', methods=['GET']) #DONE-TESTED
@token_required
def get_consumption_day(id, area_name):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()

    if area_name is None:
        return "Invalid area name", 400

    try:
        format="%F %T"
        req_time = parse_timestamp()
        next_day = req_time + timedelta(days=1)
        req_time = req_time.strftime(format)
        next_day = next_day.strftime(format)
        
        res = query(cursor, 'SELECT * FROM consumptions WHERE USERNAME=(\'%s\') AND AREA_NAME=(\'%s\') AND timestamp <= \'%s\' AND timestamp >= \'%s\' ORDER BY timestamp DESC LIMIT 24',
                    (id, area_name, next_day, req_time))
        
    except Exception as e:
        return "Area '%s' with difficulties" % area_name, 400

    conn.commit()
    conn.close()
    
    total_energy = sum([row[4] for row in res])
    total_water = sum([row[5] for row in res])
    total_gas = sum([row[6] for row in res])

    result = {
        "total_energy": total_energy,
        "total_water": total_water,
        "total_gas": total_gas
    }

    return jsonify(result), 200

@app.route('/consumptions/<area_name>', methods=['POST']) #DONE-TESTED
@token_required
def create_consumptions(id, area_name):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()

    if area_name is None:
        return "Invalid area name", 400

    format="%F %T"
    request_time = parse_timestamp().strftime(format)
    request_data = parse_qs(request.get_data().decode('utf-8'))
    energy_amount = request_data.get('energy', [])[0]
    water_amount = request_data.get('water', [])[0]
    gas_amount = request_data.get('gas', [])[0]
    at_home = request_data.get('at_home', [])[0]
    
    
    if request_time is None:
        try:
            cons = Consumption(area=area_name)
            query(cursor, 'INSERT INTO consumptions (username, area_name, at_home, energy, water, gas) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\')',
                    (id, cons.area, cons.at_home, cons.energy.amount, cons.water.amount, cons.gas.amount))
        
        except Exception as e:
            return "Area '%s' already exists" % area_name, 400
    else:
        try:
            cons = Consumption(area=area_name, timestamp=request_time, energy=energy_amount, water=water_amount, gas=gas_amount, at_home=at_home)
            query(cursor, 'INSERT INTO consumptions (username, area_name, at_home, energy, water, gas, timestamp) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\')',
                    (id, cons.area, cons.at_home, cons.energy.amount, cons.water.amount, cons.gas.amount, cons.timestamp))
        except Exception as e:
            return "Area '%s' already exists" % area_name, 400

    conn.commit()
    conn.close()
    return "Ok", 200

@app.route('/consumptions/<area_name>/', methods=['GET']) #DONE-TESTED
@token_required
def get_consumption(id, area_name):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()

    if area_name is None:
        return "Invalid area name", 400

    try:
        format="%F %T"
        req_time = parse_timestamp().strftime(format)
        
        res = query(cursor, 'SELECT * FROM consumptions WHERE USERNAME=(\'%s\') AND AREA_NAME=(\'%s\') AND timestamp <= \'%s\' ORDER BY timestamp DESC LIMIT 1',
                    (id, area_name, req_time))
        
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
    password = request_data.get('pass', [])[0]
    email = request_data.get('email', [])[0]
    temp_max = request_data.get('temp_max', [])[0]
    temp_min = request_data.get('temp_min', [])[0]
    
    if None in (username, password):
        return "invalid username or password", 400

    hashed = hash_password(username, password)

    try:
        query(cursor, 'INSERT INTO users (username, pass, email, temp_max, temp_min) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\')', (username, hashed, email, temp_max, temp_min))
    except Exception as e:
        return "Username '%s' already exists" % username, 400

    conn.commit()
    cursor.close()
    conn.close()
    return "Ok", 200

@app.route('/users/', methods=["DELETE"]) #DONE-TESTED
@token_required
def delete_user(id):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()

    if id is None:
        return "Invalid username", 400

    try:
        query(cursor, 'DELETE FROM users WHERE username=(\'%s\')', (id))
    except:
        return "Username '%s' cannot be deleted" % id, 400

    conn.commit()
    cursor.close()
    conn.close()
    return "Ok", 200

@app.route('/users/<username>/temperature', methods=["PUT"]) #DONE-TESTED
@token_required
def update_temperature(id, username):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()

    request_data = parse_qs(request.get_data().decode('utf-8'))
    temp_max = request_data.get('temp_max', [])[0]
    temp_min = request_data.get('temp_min', [])[0]
    
    try:
        query(cursor, 'UPDATE users SET temp_max = \'%s\', temp_min = \'%s\' WHERE username = \'%s\'', (temp_max, temp_min, username))
    except Exception as e:
        return "Couldn't change the temperature range", 400
    
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

@app.route('/events/', methods=['GET', 'POST', 'DELETE'])
@token_required
def manage_calendar(id):

    if request.method == 'POST':    #DONE-TESTED
        conn = sqlite3.connect(DATABASENAME)
        cursor = conn.cursor()
        
        format="%F %T"
        date = parse_timestamp().strftime(format)
        request_data = parse_qs(request.get_data().decode('utf-8'))
        title = request_data.get('title', [])[0]
        description = request_data.get('description', [])[0]
        #warning = request.form["warning"]
        
        try:
            query(cursor, "INSERT INTO events (username, date, title, description) VALUES (\'%s\', \'%s\', \'%s\', \'%s\')", (id, date, title, description))
        except Exception as e:
            return "Event already exists", 400

        conn.commit()
        cursor.close()
        conn.close()
        return "Ok", 200
    
    elif request.method == 'GET':   #DONE-TESTED
        conn = sqlite3.connect(DATABASENAME)
        cursor = conn.cursor()
        
        request_data = parse_qs(request.get_data().decode('utf-8'))
        year = request_data.get('year1', [])[0]
        month = request_data.get('month1', [])[0]
        day = request_data.get('day1', [])[0]
        hour = request_data.get('hours1', [])[0]
        date = datetime(int(year), int(month), int(day), int(hour), int(0), int(0))
        
        request_data = parse_qs(request.get_data().decode('utf-8'))
        year = request_data.get('year2', [])[0]
        month = request_data.get('month2', [])[0]
        day = request_data.get('day2', [])[0]
        hour = request_data.get('hours2', [])[0]
        next_date = datetime(int(year), int(month), int(day), int(hour), int(0), int(0))
        
        res = query(cursor, "SELECT * FROM events WHERE date > \'%s\' AND date < \'%s\' AND username = (\'%s\')", (date, next_date, id))
        
        if res:
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify(res), 200
        else:
            conn.commit()
            cursor.close()
            conn.close()
            return "No event not found", 200
    
    elif request.method == 'DELETE':    #DONE-TESTED
        conn = sqlite3.connect(DATABASENAME)
        cursor = conn.cursor()
        
        request_data = parse_qs(request.get_data().decode('utf-8'))
        title = request_data.get('title', [])[0]
        
        try:
            query(cursor, "DELETE FROM events WHERE title = (\'%s\') AND username = (\'%s\')", (title, id))
            conn.commit()
            cursor.close()
            conn.close()
            return "Event deleted successfully", 200
        except Exception as e:
            return "Event not found", 404
    
    return "Method not implemented", 501

def email_reminder():
    while True:
        conn = sqlite3.connect(DATABASENAME)
        cursor = conn.cursor()
        current_time = datetime.now()        
        try:
            res = query(cursor, "SELECT * FROM events")
        except Exception as e:
            pass
        
        user_calendars = {}
        for row in res:
            user = row[0]
            date = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
            title = row[2]
            description = row[3]
            
            if user not in user_calendars:
                user_calendars[user] = Calendar()
            user_calendars[user].add_event(Event(title, date, description))
            
        for user, calendar in user_calendars.items():
            aux = Send_Email(calendar, current_time)
            try:
                res = query(cursor, "SELECT email FROM users WHERE username = (\'%s\')", (user))
            except Exception as e:
                pass
            Send_Email.send_reminder_emails(aux, recipient_email=res[0][0])
        
        conn.commit()
        cursor.close()
        conn.close()
        time.sleep(3600*24)  # Sleep for 24 hour

if __name__ == '__main__':
    SCHEMANAME = os.path.dirname(os.path.realpath(__file__)) + "/schema.sql"
    
    if not os.path.exists(DATABASENAME):
            connection = sqlite3.connect(DATABASENAME)

            with open(SCHEMANAME, "r") as f:
                connection.executescript(f.read())

            connection.commit()
            connection.close()
    
    send_email_thread = threading.Thread(target=email_reminder)
    send_email_thread.start()
            
    app.run(debug=True)