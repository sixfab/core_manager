#!/usr/bin/python3

from helpers.logger import logger
from modules.network import Network

network = Network()


def manage_network():
    network.check_interfaces()
    network.get_interface_metrics()
    network.check_and_create_monitoring()

    try:
        network.adjust_priorities()
    except Exception as error:
        logger.critical("adjust_priorities() --> %s", error)

    network.debug_routes()


if __name__ == "__main__":
    manage_network()
