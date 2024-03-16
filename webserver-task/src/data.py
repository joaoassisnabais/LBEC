import json
import sqlite3
import os
import datetime

class Dto:
    def to_json(self) -> str:
        raise NotImplementedError()

class Info:
    def __init__(self, latitude, longitude, speed, time):
        self.latitude = latitude
        self.longitude = longitude
        self.speed = speed
        self.time = time

    def get_latitude(self):
        return self.latitude

    def get_longitude(self):
        return self.longitude

    def get_speed(self):
        return self.speed

    def get_time(self):
        return self.time

class InfosDto(Dto):
    def infotime_to_seconds(info):
        """
        Takes an info instance and returns the seconds in it's timestamp
        Use to sort lists
        """
        time = info.time
        
        try:
            FMT = "%H:%M:%S.%f"
            a = datetime.datetime.strptime(time, FMT)
        except ValueError:
            FMT = "%H:%M:%S"
            a = datetime.datetime.strptime(time, FMT)

        return (datetime.datetime.combine(datetime.date.min, a.time()) - datetime.datetime.min).total_seconds()

    def __init__(self, infos: list):
        infos.sort(key = InfosDto.infotime_to_seconds)

        self.data = {"Latitude": [], "Longitude": [], "Speed": [], "Time": []}

        for info in infos:
            self.data["Latitude"].append(info.get_latitude())
            self.data["Longitude"].append(info.get_longitude())
            self.data["Speed"].append(info.get_speed())
            self.data["Time"].append(info.get_time())

    def to_json(self) -> str:
        return json.dumps(self.data)

class Repository:
    def add(self, obj):
        raise NotImplementedError()

    def get(self, identifier):
        raise NotImplementedError()

    def getAll(self) -> list:
        raise NotImplementedError()

    def delete(self, identifier):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

class InfoRepoLocal(Repository):
    class Entry:
        def __init__(self, identifier, info: Info):
            self.id = identifier
            self.info = info

    def __init__(self):
        self.infos = []
        self.count = 0

    def add(self, obj):
        self.infos.append(self.Entry(self.count, obj))
        self.count += 1

    def get(self, identifier):
        return next(x for x in self.infos if x.id == identifier)

    def delete(self, identifier):
        self.infos = list(filter(lambda x: x.id != identifier, self.infos))

    def getAll(self):
        return list(map(lambda x: x.info, self.infos))

class InfoRepoDatabase(Repository):
    DATABASENAME = os.path.dirname(os.path.realpath(__file__)) + "/database.db"
    SCHEMANAME = os.path.dirname(os.path.realpath(__file__)) + "/schema.sql"

    def __init__(self):
        if not os.path.exists(self.DATABASENAME):
            connection = sqlite3.connect(self.DATABASENAME)

            with open(self.SCHEMANAME, "r") as f:
                connection.executescript(f.read())

            connection.commit()
            connection.close()

    def add(self, obj):
        connection = sqlite3.connect(self.DATABASENAME)
        cursor = connection.cursor()

        cursor.execute("INSERT INTO infos (latitude, longitude, speed, time) VALUES (?, ?, ?, ?)",
                    (obj.latitude, obj.longitude, obj.speed, obj.time))

        connection.commit()
        connection.close()


    def get(self, identifier):
        connection = sqlite3.connect(self.DATABASENAME)
        cursor = connection.cursor()

        ret = list(cursor.execute("SELECT * FROM infos WHERE id=:identifier", {"identifier": identifier}))[0]

        connection.close()
        return ret

    def delete(self, identifier):
        connection = sqlite3.connect(self.DATABASENAME)
        cursor = connection.cursor()

        ret = list(cursor.execute("DELETE FROM infos WHERE id=:identifier", {"identifier": identifier}))

        connection.commit()
        connection.close()

    def getAll(self):
        connection = sqlite3.connect(self.DATABASENAME)
        cursor = connection.cursor()

        ret = list(cursor.execute("SELECT * FROM infos"))

        connection.close()

        return list(map(lambda x: Info(x[1], x[2], x[3], x[4]), ret))

