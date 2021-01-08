#!/usr/bin/python3

import time
import platform 
import usb.util
import usb.core

from helpers.serial import send_at_com
from helpers.config import read_config, save_system_id
from helpers.logger import initialize_logger
from helpers.exceptions import *

from modules.configure_modem import configure_modem
from modules.check_network import check_network
from modules.reconnect import initiate_ecm, check_internet, reconnect
from modules.identify_setup import identify_setup

logger = initialize_logger(True)

logger.info("Connection Manager started.")
send_at_com("ATE0", "OK") # turn off modem input echo

identify_setup()

try:
    configure_modem()
except ModemNotSupported:
    pass
except ModemNotFound:
    pass
except Exception as e:
    log.error(str(e))

check_network()
initiate_ecm(1)

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

