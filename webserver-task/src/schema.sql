DROP TABLE IF EXISTS infos;

CREATE TABLE infos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude INTEGER NOT NULL,
    longitude INTEGER NOT NULL,
    speed INTEGER NOT NULL,
    time TEXT NOT NULL
);
