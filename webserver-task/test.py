#!/bin/env python3

import random
import time 
import requests
import datetime
import multiprocessing
import os

url = 'http://localhost:5000'
cross = u'\u274C'
tick = u'\u2705'
jobs_num = 10 # number of client (avoid going above number of cpu cores)
num_iter = 20 # number of requests done for each client
code_ok = 200

def gen_data():
        lat = random.randint(387365578, 387367578)
        lon = random.randint(-91389050, -91379050)
        time_record = str(datetime.datetime.utcnow().time())
        speed = random.randint(0,80)
        return lat, lon, time_record, speed

def insert_post():
        lat, lon, time_record, speed = gen_data()
        data = ('Latitude', lat), ('Longitude', lon),('Time', time_record), ('Speed', speed)
        x = requests.post(url+'/put_data', data=data)
        return x.status_code

def insert_get():
        lat, lon, time_record, speed = gen_data()
        data = f'?Latitude={lat}&Longitude={lon}&Time={time_record}&Speed={speed}'
        x = requests.get(url+'/put_data'+data)
        return x.status_code

def get_data():
        x = requests.get(url+'/get_data')
        return x.status_code

def run(func, num_requests):        
    counter = 0
    request_type = func.__name__
    start = time.time()
    for i in range(num_requests):
        code = func()
        if(code == code_ok):
                counter += 1
        else:
                print(f'[{code}] - Client {os.getpid()} - {request_type}')
        time.sleep(random.random()) #sleep between 0 and 1 second
    end = time.time()
    timer = end - start
    symbol = tick if counter == num_requests else cross
    print(f'[{symbol}] [TIME]: {timer} - Client {os.getpid()} {counter}/{num_requests} {request_type}')


def create_runners(func, num_requests):
        jobs = []
        for i in range(jobs_num):
                p = multiprocessing.Process(target=run, args=(func, num_requests,))
                p.start()
                jobs.append(p)
        return jobs

if __name__ == '__main__':
        insert_get_jobs = create_runners(insert_get, num_iter)
        insert_post_jobs = create_runners(insert_post, num_iter)

        start = time.time()
        for job in range(jobs_num):
                insert_get_jobs[job].join()
                insert_post_jobs[job].join()
        run(get_data, 1)
        end = time.time()
        timer = end - start
        print(f'[Total Time]: {timer}')
