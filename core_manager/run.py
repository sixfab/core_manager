#!/usr/bin/python3

import time
from threading import Thread, Lock

from cm import manage_connection
from nm import manage_network
from monitor import monitor
from configurator import configure
from helpers.config_parser import logger

lock = Lock()

def thread_manage_connection():
    interval = 0
    while(True):
        with lock:
            interval = manage_connection() 
        time.sleep(interval)

def thread_monitor_and_config():
    while(True):
        with lock:
            configure()
            manage_network()
            interval = monitor()
        time.sleep(20)

def main():
    Thread(target=thread_manage_connection).start()
    Thread(target=thread_monitor_and_config).start()

if __name__ == "__main__":
    main()


