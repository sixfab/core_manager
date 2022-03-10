#!/usr/bin/python3

from helpers.logger import logger
from modules.network import Network
from helpers.modem_support.telit import Telit

def manage_network(modem):
    network = Network(modem)
    network.check_interfaces()
    network.get_interface_metrics()
    network.get_interface_type()
    network.get_interface_priority()
    network.check_and_create_monitoring()

    try:
        network.adjust_priorities()
    except Exception as error:
        logger.error("adjust_priorities() --> %s", error)

    network.debug_routes()

    return network

if __name__ == "__main__":
    import time
    modem = Telit()
    while True:
        network = Network(modem)
        network.check_interfaces()
        network.get_interface_metrics()
        network.get_interface_type()
        network.adjust_priorities()
        network.get_interface_priority()
        network.check_and_create_monitoring()
        time.sleep(5)
