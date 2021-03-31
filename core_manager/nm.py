#!/usr/bin/python3

import time

from helpers.logger import logger
from modules.network import Network


network = Network()

def manage_network():
    network.check_interfaces()
    network.check_and_create_monitoring()
    
    try:
        network.adjust_priorities()
    except Exception as e:
        logger.critical("adjust_priorities() --> " + str(e))
        
    network.debug_routes()

if __name__  == "__main__":
    manage_network()