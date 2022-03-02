#!/usr/bin/python3

from helpers.logger import logger
from modules.network import Network


def manage_network(modem):
    network = Network(modem)
    network.check_interfaces()
    network.get_interface_metrics()
    network.check_and_create_monitoring()

    try:
        network.adjust_priorities()
    except Exception as error:
        logger.error("adjust_priorities() --> %s", error)

    network.debug_routes()

    return network
