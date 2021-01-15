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

system_info = {}
queue.set_step(0,0,0,0,0,0,0,0)

logger.info("Connection Manager started.")

while True:
    if os.path.isfile(SYSTEM_PATH):
        break
    else:
        try:
            logger.warning("system.yaml doesn't exist! Identifying the system...")
            identify_setup()
        except Exception as e:
            logger.critical(e)
            logger.critical("First identification failed. Retrying to identify required parameters!")
    time.sleep(2)

# Getting system info
try:
    system_info = read_yaml_all(SYSTEM_PATH)
except Exception as e:
    logger.critical(str(e))

modem = Modem(
    vendor = system_info.get("modem_vendor", ""),
    model = system_info.get("modem_name", ""),
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


def _organizer():
    if queue.base == 0:
        queue.sub = 1
    else:    
        if queue.is_ok == True:
            queue.sub = queue.success
            queue.is_ok = False
            queue.clear_counter()
        else:
            if queue.counter >= queue.retry:
                queue.sub = queue.kill
                queue.clear_counter()
            else:
                queue.sub = queue.fail
                queue.counter_tick()

def _identify_setup():
    global modem
    queue.set_step(sub=0, base=1, success=2, fail=1, kill=1, interval=0.1, is_ok=False, retry=5)

    try:
        new_id = identify_setup()
    except Exception as e:
        logger.error(str(e))
        queue.is_ok = False
    else:
        if new_id != 0:
            modem.update(
                vendor = new_id.get("modem_vendor", ""),
                model = new_id.get("modem_name", ""),
                imei = new_id.get("imei", ""),
                ccid = new_id.get("ccid", ""),
                sw_version = new_id.get("sw_version", ""),
                vendor_id = new_id.get("modem_vendor_id", ""),
                product_id = new_id.get("modem_product_id", "")
            ) 
        queue.is_ok = True

def _configure_modem():
    queue.set_step(sub=0, base=2, success=3, fail=2, kill=1, interval=1, is_ok=False, retry=5)

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
    queue.set_step(sub=0, base=3, success=4, fail=3, kill=1, interval=0.1, is_ok=False, retry=5)

    try:
        modem.check_network()
    except Exception as e:
        logger.error(str(e))
        queue.is_ok = False
    else:
        queue.is_ok = True

def _initiate_ecm():
    queue.set_step(sub=0, base=4, success=5, fail=4, kill=1, interval=0.1, is_ok=False, retry=5)

    try:
        modem.initiate_ecm()
    except Exception as e:
        logger.error(str(e))
        queue.is_ok = False
    else:
        queue.is_ok = True

def _check_internet():
    queue.set_step(sub=0, base=5, success=5, fail=6, kill=1, interval=10, is_ok=False, retry=0)

    try:
        modem.check_internet()
    except Exception as e:
        logger.error(str(e))
        queue.is_ok = False
    else:
        print(".", end="", flush=True)  # debug purpose
        queue.is_ok = True

def _double_check_internet():
    queue.set_step(sub=0, base=6, success=5, fail=7, kill=1, interval=10, is_ok=False, retry=0)

    try:
        modem.check_internet()
    except Exception as e:
        logger.error(str(e))
        queue.is_ok = False
    else:
        print("/", end="", flush=True)  # debug purpose
        queue.is_ok = True

def _diagnose():
    queue.set_step(sub=0, base=7, success=8, fail=7, kill=1, interval=0.1, is_ok=False, retry=5)

    try:
        modem.diagnose()
    except Exception as e:
        logger.error(str(e))
        queue.is_ok = False
    else:
        queue.is_ok = True

def _reconnect():
    queue.set_step(sub=0, base=8, success=3, fail=8, kill=1, interval=0.1, is_ok=False, retry=5)

    try:
        modem.reconnect()
    except Exception as e:
        logger.error(str(e))
        queue.is_ok = False
    else:
        queue.is_ok = True

def _reset_modem_softly():
    queue.set_step(sub=0, base=9, success=3, fail=9, kill=1, interval=0.1, is_ok=False, retry=5)

    try:
        modem.reset_modem_softly()
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
    9: _reset_modem_softly,
}
    
def execute_step(x):
    steps.get(x)()

def manage_connection():
    execute_step(queue.sub)
    return queue.interval

if __name__  == "__main__":
    while True:
        interval = manage_connection()
        time.sleep(interval)