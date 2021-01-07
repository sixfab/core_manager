#!/usr/bin/python3

import time

from helpers.serial import send_at_com
from helpers.config import read_config
from helpers.logger import initialize_logger

from modules.configure_modem import configure_modem
from modules.check_network import check_network
from modules.reconnect import initiate_ecm, check_internet, reconnect

import usb

logger = initialize_logger(True)

logger.info("Connection Manager is started...")

configure_modem()
check_network()
initiate_ecm(1)

while True:  
    
    internet = False

    if check_internet() == 0:
        internet = True
        print(".")
    else:
        # double check
        print("/")
        if check_internet() == 0:
            internet = True
        else:
            internet = False
    
    if internet == False:
        reconnect(1)

    time.sleep(5)

