#!/usr/bin/python3

from threading import Thread, Lock, Event

from helpers.config_parser import conf
from helpers.logger import logger
from helpers.modem_support.default import BaseModule

from cm import manage_connection
from nm import manage_network
from monitor import monitor
from configurator import configure
from geolocation import update_geolocation


lock = Lock()
event = Event()
modem = BaseModule()

def thread_manage_connection(event_object):
    global modem
    interval = 0
    while True:
        with lock:
            res = manage_connection()
            if not isinstance(res, tuple):
                interval = res
            else:
                interval = res[0]
                modem = res[1]
                print(interval, modem)
        event_object.wait(interval)


def thread_monitor_and_config(event_object):
    global modem
    while True:
        with lock:
            logger.debug("Configurator is working...")
            configure()
            logger.debug("Network manager is working...")
            network = manage_network(modem)
            logger.debug("Monitor is working...")
            monitor(modem, network)
            logger.debug("Geolocation is working...")
            update_geolocation(modem)
        event_object.wait(conf.get_send_monitoring_data_interval_config())


def main():
    Thread(target=thread_manage_connection, args=(event,)).start()
    Thread(target=thread_monitor_and_config, args=(event,)).start()


if __name__ == "__main__":
    main()
