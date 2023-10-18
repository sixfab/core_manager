#!/usr/bin/python3

from helpers.logger import logger
from modules.network import Network


def manage_network(modem):
    network = Network(modem)
    network.check_interfaces()
    network.get_interface_metrics()
    network.get_interface_type()
    network.check_connection_status()

    try:
        network.adjust_priorities()
    except Exception as error:
        logger.error("adjust_priorities() --> %s", error)

    network.get_interface_priority()
    network.create_monitoring_data()
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
        network.check_connection_status()
        network.adjust_priorities()
        network.get_interface_priority()
        network.create_monitoring_data()
        network.debug_routes()
        time.sleep(5)
