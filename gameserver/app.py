from flask import Flask, request
from functools import wraps
from hashlib import sha256
import psycopg2
import psycopg2.extras
import json
import jwt
import datetime
import os
from applog import log
import subprocess
from data import TokenDto
    

CWD = os.path.dirname(__file__)
app = Flask(__name__)

credentials = json.load(open(os.path.join(CWD, "creds.json"), "r"))

DB_CONNECTION_STRING = "host=%s dbname=%s user=%s password=%s" % (credentials["DB_HOST"], credentials["DB_DATABASE"], credentials["DB_USER"], credentials["DB_PASSWORD"])

def query(cursor, string, data = ()):
    res = []
    cursor.execute(string, data)
    
    try:
        for row in cursor:
            res.append(row)
    except Exception as e:
        pass

    return res

def transaction(cursor):
    query(cursor, "START TRANSACTION;")

def commit(cursor):
    query(cursor, "COMMIT;")

def user_exists(username):
    dbConn = psycopg2.connect(DB_CONNECTION_STRING)
    cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    res = query(cursor, 'SELECT * FROM users WHERE name=(%s)', (username,))

    dbConn.commit()
    cursor.close()
    dbConn.close()

    return res != []

def is_admin(username):
    dbConn = psycopg2.connect(DB_CONNECTION_STRING)
    cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    res = query(cursor, 'SELECT * FROM admins WHERE name=(%s)', (username,))

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

def admin_required(f):
    @wraps(f)
    def admin_dec(*args, **kwargs):
        id = kwargs["id"]

        if not is_admin(id):
            return "No permission", 400

        return f(*args, **kwargs)
    return admin_dec

def hash_password(username, password):
    return str(sha256((password + credentials["APPKEY"] + username).encode("UTF-8")).hexdigest())

@app.route('/users/<username>', methods=["POST"])
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
@admin_required
def delete_user(id, username):
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

@app.route('/games/<name>', methods=["POST"])
@token_required
def create_game(id, name):
    dbConn = psycopg2.connect(DB_CONNECTION_STRING)
    cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        query(cursor, 'INSERT INTO games (name, created_by) VALUES (%s, %s)', (name, id))
    except psycopg2.errors.UniqueViolation as e:
        return "Game '%s' already exists" % name, 400
    except Exception as e:
        log(e)
        return "Unkown error", 400

    dbConn.commit()
    cursor.close()
    dbConn.close()

    return "Ok", 200

@app.route('/games/<name>', methods=["DELETE"])
@token_required
def delete_game(id, name):
    dbConn = psycopg2.connect(DB_CONNECTION_STRING)
    cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        res = query(cursor, 'SELECT * FROM games WHERE name=(%s) AND created_by=(%s)', (name, id))
        if res == [] and not is_admin(id): # admins can delete any game
            return "No permission", 400

        query(cursor, 'DELETE FROM games WHERE name=(%s)', (name,))
    except Exception as e:
        return "Unkown error", 400

    dbConn.commit()
    cursor.close()
    dbConn.close()

    return "Ok", 200

@app.route('/games/<game>/join', methods=["POST"])
@token_required
def join_game(id, game):
    dbConn = psycopg2.connect(DB_CONNECTION_STRING)
    cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        query(cursor, 'INSERT INTO game_players (player_name, game_id) VALUES (%s, %s)', (id, game))
    except psycopg2.errors.UniqueViolation as e:
        return "User '%s' is already in the game '%s'" % (id, game), 400
    except Exception as e:
        return "Unkown error", 400

    dbConn.commit()
    cursor.close()
    dbConn.close()

    return "Ok", 200

@app.route('/games/<game>/leave', methods=["POST"])
@token_required
def leave_game(id, game):
    dbConn = psycopg2.connect(DB_CONNECTION_STRING)
    cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        query(cursor, 'DELETE FROM game_players WHERE player_name=(%s) AND game_id=%s', (id, game))
    except Exception as e:
        return "Unkown error", 400

    dbConn.commit()
    cursor.close()
    dbConn.close()

    return "Ok", 200

@app.route('/login', methods=["GET"])
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
        exp = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
        token = jwt.encode({'user' : userAuth.username, 'exp' : exp}, credentials['APPKEY'], algorithm="HS256")
        return TokenDto(token, exp).to_json(), 200
    return "Invalid credentials", 400

@app.route('/admin/users/<user>', methods=["GET"])
@token_required
@admin_required
def user_info(id, user):
    dbConn = psycopg2.connect(DB_CONNECTION_STRING)
    cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        res = query(cursor, 'SELECT * FROM users WHERE name=(%s)', (user,))[0]
    except IndexError as e:
        return "User does not exist", 400
    except:
        return "Unkown Error", 400

    dbConn.close()
    cursor.close()

    return str(tuple(res) + (is_admin(user),)), 200

@app.route('/admin/dbcmd', methods=["GET"])
@token_required
@admin_required
def database_cmd(id):
    dbConn = psycopg2.connect(DB_CONNECTION_STRING)
    cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cmd = request.args.get('cmd')

    if not cmd:
        return "Empty cmd", 400

    try:
        res = query(cursor, cmd)
    except Exception as e:
        return str(e), 400

    return str(res), 200

@app.route('/admin/reload', methods=["GET"])
@token_required
@admin_required
def reload(id):
    dbConn = psycopg2.connect(DB_CONNECTION_STRING)
    cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        res = subprocess.run(["bash", "./" + os.path.join(CWD, "scripts", "reload")])
    except Exception as e:
        return str(e), 400

    return str(res), 200

@app.route('/')
@token_required
def hello_world(id):
   return "hello %s!" % id 

if __name__ == "__main__":
    app.run(ssl_context=("/etc/letsencrypt/live/ruipires.ddns.net/cert.pem", "/etc/letsencrypt/live/ruipires.ddns.net/privkey.pem"))
