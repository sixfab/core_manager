#!/usr/bin/python3

from threading import Thread, Lock, Event

from helpers.config_parser import conf
from helpers.logger import logger

from cm import manage_connection
from nm import manage_network
from monitor import monitor
from configurator import configure


lock = Lock()
event = Event()


def thread_manage_connection(event_object):
    interval = 0
    while True:
        with lock:
            interval = manage_connection()
        event_object.wait(interval)


def thread_monitor_and_config(event_object):
    while True:
        with lock:
            logger.debug("Configurator is working...")
            configure()
            logger.debug("Network manager is working...")
            manage_network()
            logger.debug("Monitor is working...")
            monitor()
        event_object.wait(conf.get_send_monitoring_data_interval_config())


def main():
    Thread(target=thread_manage_connection, args=(event,)).start()
    Thread(target=thread_monitor_and_config, args=(event,)).start()


if __name__ == "__main__":
    main()
