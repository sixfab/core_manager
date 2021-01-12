#!/usr/bin/python3

import time
import os.path

from helpers.commander import send_at_com
from helpers.yamlio import *
from helpers.exceptions import *
from helpers.config_parser import *
from helpers.queue import queue

from modules.identify import identify_setup
from modules.modem import Modem


# Check the system file exist.
if os.path.isfile(SYSTEM_PATH):
    pass
else:
    try:
        identify_setup()
    except Exception as e:
        logger.critical(str(e))
        logger.critical("First identification failed. Program is exiting!")
        exit(1)

logger.info("Connection Manager started.")

# Start step
queue.set_step(0,0,0,0,0,0)

modem = Modem(
    vendor = system_info.get("modem_vendor", ""),
    model = "EC25",
    imei = system_info.get("imei", ""),
    ccid = system_info.get("ccid", ""),
    sw_version = system_info.get("sw_version", ""),
    vendor_id = system_info.get("modem_vendor_id", ""),
    product_id = system_info.get("modem_product_id", "")
)

if DEBUG == True and VERBOSE_MODE == True:
    print("")
    print("********************************************************************")
    print("[?] MODEM REPORT")
    print("-------------------------")
    attrs = vars(modem)
    print('\n'.join("[+] %s : %s" % item for item in attrs.items()))
    print("********************************************************************")
    print("")
    #exit()

def _organizer():
    if queue.base == 0:
        queue.sub = 1
    else:    
        # print("Base: " + str(queue.base) + "\tSub: " + str(queue.sub))
        if queue.is_ok == True:
            queue.sub = queue.success
            queue.is_ok = False
        else:
            queue.sub = queue.fail

def _identify_setup():
    queue.set_step(sub=0, base=1, success=2, fail=1, interval=0.1, is_ok=False)

    try:
        identify_setup()
    except Exception as e:
        logger.error(str(e))
        queue.is_ok = False
    else:
        queue.is_ok = True

def _configure_modem():
    queue.set_step(sub=0, base=2, success=3, fail=2, interval=0.1, is_ok=False)

    try:
        modem.configure_modem()
    except ModemNotSupported:
        queue.is_ok = False
    except ModemNotFound:
        queue.is_ok = False
    except Exception as e:
        logger.error(str(e))
        queue.is_ok = False
    else:
        queue.is_ok = True

def _check_network():
    queue.set_step(sub=0, base=3, success=4, fail=3, interval=0.1, is_ok=False)

    try:
        modem.check_network()
    except Exception as e:
        logger.error(str(e))
        queue.is_ok = False
    else:
        queue.is_ok = True

def _initiate_ecm():
    queue.set_step(sub=0, base=4, success=5, fail=4, interval=0.1, is_ok=False)

    try:
        modem.initiate_ecm()
    except Exception as e:
        logger.error(str(e))
        queue.is_ok = False
    else:
        queue.is_ok = True

def _check_internet():
    queue.set_step(sub=0, base=5, success=5, fail=6, interval=5, is_ok=False)

    try:
        modem.check_internet()
    except Exception as e:
        logger.error(str(e))
        queue.is_ok = False
    else:
        print(".", end="", flush=True)  # debug purpose
        queue.is_ok = True

def _double_check_internet():
    queue.set_step(sub=0, base=6, success=5, fail=7, interval=5, is_ok=False)

    try:
        modem.check_internet()
    except Exception as e:
        logger.error(str(e))
        queue.is_ok = False
    else:
        print("/", end="", flush=True)  # debug purpose
        queue.is_ok = True

def _diagnose():
    queue.set_step(sub=0, base=7, success=8, fail=7, interval=0.1, is_ok=False)

    try:
        modem.diagnose()
    except Exception as e:
        logger.error(str(e))
        queue.is_ok = False
    else:
        queue.is_ok = True

def _reconnect():
    # Identify setup
    queue.set_step(sub=0, base=8, success=3, fail=8, interval=0.1, is_ok=False)

    try:
        modem.reconnect()
    except Exception as e:
        logger.error(str(e))
        queue.is_ok = False
    else:
        queue.is_ok = True

steps = {
    0: _organizer, 
    1: _identify_setup,
    2: _configure_modem,
    3: _check_network,
    4: _initiate_ecm,
    5: _check_internet,
    6: _double_check_internet,
    7: _diagnose,
    8: _reconnect,
}
    
def execute_step(x):
    steps.get(x)()

while(True):
    execute_step(queue.sub)
    time.sleep(queue.interval)