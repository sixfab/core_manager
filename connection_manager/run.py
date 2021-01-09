#!/usr/bin/python3

import time
import platform 
import usb.util
import usb.core

from helpers.serial import send_at_com
from helpers.config import *
from helpers.logger import initialize_logger
from helpers.exceptions import *

from modules.modem import configure_modem, check_network
from modules.reconnect import initiate_ecm, check_internet, reconnect
from modules.identify import identify_setup

logger = initialize_logger(True)

logger.info("Connection Manager started.")

# Endless loop
while True:  
    
    internet = False

    if check_internet() == 0:
        internet = True
        print(".", end="", flush=True)
    else:
        # double check
        print("/", end="", flush=True)
        if check_internet() == 0:
            internet = True
        else:
            internet = False
    
    if internet == False:
        reconnect(1)

    time.sleep(5)

