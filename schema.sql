drop table if exists users;
drop table if exists consumptions;
drop table if exists events;

-- Create the User table
CREATE TABLE users (
  username VARCHAR(255) UNIQUE NOT NULL,
  pass VARCHAR(255) NOT NULL
);

-- Create the Consumption table
CREATE TABLE consumptions (
  username VARCHAR(255) NOT NULL,
  area_name VARCHAR(255) NOT NULL,
  at_home BIT,
  timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  energy FLOAT NOT NULL,
  water FLOAT NOT NULL,
  gas FLOAT NOT NULL,
  
  FOREIGN KEY (username) REFERENCES user(username)
);

-- Create the Event table
CREATE TABLE events (
  username VARCHAR(255) NOT NULL,
  date DATETIME NOT NULL,
  title VARCHAR(255) NOT NULL,
  description VARCHAR(255),
  
  FOREIGN KEY (username) REFERENCES user(username)
);