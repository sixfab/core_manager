#!/usr/bin/python3

import time
from threading import Thread, Lock

from cm import manage_connection
from helpers.config_parser import logger

logger.info("Connection Manager started.")

lock = Lock()

def worker1():
    while(True):
        with lock:
            print("Worker 1")
            time.sleep(1)

def worker2():
    while(True):
        with lock:
            print("worker 2")
        time.sleep(2)

def main():
    Thread(target=worker1).start()
    Thread(target=worker2).start()

main()


