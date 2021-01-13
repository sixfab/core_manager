#!/usr/bin/python3

import time
from threading import Thread, Lock

from helpers.logger import initialize_logger

logger = initialize_logger(True)
logger.info("Connection Manager started.")

lock = Lock()

def worker1():
    while(True):

        with lock:
            print("worker 1")
        time.sleep(4)

def worker2():
    while(True):
        with lock:
            print("worker 2")
        time.sleep(2)

def main():
    Thread(target=worker1).start()
    Thread(target=worker2).start()

main()


