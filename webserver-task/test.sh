#!/bin/sh

curl -X POST -F 'Latitude=387366743' -F 'Longitude=-91398238' -F 'Time=12:35:13' -F 'Speed=25' http://localhost:5000/put_data & curl -X POST -F 'Latitude=387366468' -F 'Longitude=-91398209' -F 'Time=12:35:14' -F 'Speed=30' http://localhost:5000/put_data & curl -X POST -F 'Latitude=387366292' -F 'Longitude=-91398214' -F 'Time=12:35:15' -F 'Speed=35' http://localhost:5000/put_data

curl "http://localhost:5000/get_data"
echo
