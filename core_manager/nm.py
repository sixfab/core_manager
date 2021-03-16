#!/usr/bin/python3

from modules.network import Network
from helpers.config_parser import logger

network = Network()
usable_interfaces = []

def manage_network():
    
    network.check_and_create_monitoring()

    #logger.info("Priorities are adjusting...")
    
    try:
        network.adjust_priorities()
    except Exception as e:
        logger.critical("adjust_priorities() --> " + str(e))
        
    network.debug_routes()

if __name__  == "__main__":
    manage_network()
