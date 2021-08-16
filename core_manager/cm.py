#!/usr/bin/python3

import time
import os.path

from helpers.config_parser import conf
from helpers.logger import logger
from helpers.commander import send_at_com
from helpers.yamlio import read_yaml_all, SYSTEM_PATH
from helpers.exceptions import ModemNotFound, ModemNotSupported
from helpers.queue import Queue

from modules.identify import identify_setup
from modules.modem import Modem

queue = Queue()
modem = Modem()

NO_WAIT_INTERVAL = 0.1
SECOND_CHECK_INTERVAL = 10

logger.info("Core Manager started.")


def _organizer(arg):
    #print("Organizer")
    if queue.base == 0:
        queue.sub = 1
    else:    
        if queue.is_ok == True:
            queue.sub = queue.success
            queue.is_ok = False    
        else:
            #print("Q_Counter: ", queue.counter, " Q_Retry: ", queue.retry)
            if queue.counter >= queue.retry:
                queue.sub = queue.fail
                queue.clear_counter()
                #print("***Do not wait if last retry***")
                queue.interval = 0.1
            else:
                queue.sub = queue.base
                queue.counter_tick()

                # Exception for the second chance of internet control
                if queue.base == 5:
                    #print("***Second check activated!***")
                    queue.interval = SECOND_CHECK_INTERVAL


def _identify_setup(arg):
    global modem
    queue.set_step(sub=0, base=1, success=2, fail=15, interval=2, is_ok=False, retry=20) 
    
    try:
        new_id = identify_setup()
    except Exception as e:
        logger.error("identify_setup -> " + str(e))
        queue.is_ok = False
    else:
        if new_id != {}:
            modem.update(
                vendor = new_id.get("modem_vendor", ""),
                model = new_id.get("modem_name", ""),
                imei = new_id.get("imei", ""),
                iccid = new_id.get("iccid", ""),
                sw_version = new_id.get("sw_version", ""), 
                vendor_id = new_id.get("modem_vendor_id", ""),
                product_id = new_id.get("modem_product_id", "")
            ) 
        queue.is_ok = True

        if conf.debug_mode == True and conf.verbose_mode == True:
            print("")
            print("********************************************************************")
            print("[?] MODEM REPORT")
            print("-------------------------")
            attrs = vars(modem)
            print('\n'.join("[+] %s : %s" % item for item in attrs.items()))
            print("********************************************************************")
            print("")


def _configure_modem(arg):
    queue.set_step(sub=0, base=2, success=14, fail=13, interval=1, is_ok=False, retry=5)

    try:
        modem.configure_modem()
    except ModemNotSupported:
        queue.is_ok = False
    except ModemNotFound:
        queue.is_ok = False
    except Exception as e:
        logger.error("configure_modem() -> " + str(e))
        queue.is_ok = False
    else:
        queue.is_ok = True


def _check_sim_ready(arg):
    queue.set_step(sub=0, base=14, success=3, fail=13, interval=1, is_ok=False, retry=5)

    try:
        modem.check_sim_ready()
    except Exception as e:
        logger.error("check_sim_ready() -> " + str(e))
        queue.is_ok = False
    else:
        queue.is_ok = True


def _check_network(arg):
    queue.set_step(sub=0, base=3, success=4, fail=13, interval=5, is_ok=False, retry=120)

    try:
        modem.check_network()
    except Exception as e:
        logger.error("check_network() -> " + str(e))
        queue.is_ok = False
    else:
        queue.is_ok = True


def _initiate_ecm(arg):
    queue.set_step(sub=0, base=4, success=5, fail=13, interval=0.1, is_ok=False, retry=5)

    try:
        modem.initiate_ecm()
    except Exception as e:
        logger.error("initiate_ecm() -> " + str(e))
        queue.is_ok = False
    else:
        queue.is_ok = True


def _check_internet(arg):
    #print("***Check Internet***")
    if queue.sub == 5:
        queue.set_step(sub=0, base=5, success=5, fail=6, interval=conf.check_internet_interval, is_ok=False, retry=1)
        #print("Check 1")
    elif queue.sub == 8:
        queue.set_step(sub=0, base=8, success=5, fail=9, interval=10, is_ok=False, retry=0)
        #print("Check 2")
    elif queue.sub == 10:
        queue.set_step(sub=0, base=10, success=5, fail=11, interval=10, is_ok=False, retry=0)
        #print("Check 3")

    try:
        modem.check_internet()
    except Exception as e:
        print("") # debug purpose
        logger.error("check_internet() -> " + str(e))
        queue.is_ok = False
    else:        
        if modem.incident_flag == True:
            modem.monitor["fixed_incident"] += 1
            modem.incident_flag = False

        print(".", end="", flush=True)  # debug purpose
        queue.is_ok = True


def _diagnose(arg):
    modem.monitor["cellular_connection"] = False
    modem.incident_flag = True
    diag_type = 0
    
    if queue.sub == 6:
        queue.set_step(sub=0, base=6, success=7, fail=7, interval=0.1, is_ok=False, retry=5)
        diag_type = 0
    elif queue.sub == 13:
        queue.set_step(sub=0, base=13, success=7, fail=7, interval=0.1, is_ok=False, retry=5) 
        diag_type = 1
    elif queue.sub == 15:
        queue.set_step(sub=0, base=15, success=12, fail=12, interval=0.1, is_ok=False, retry=5) 
        diag_type = 1

    try:
        modem.diagnose(diag_type)
    except Exception as e:
        logger.error("diagnose() ->" + str(e))
        queue.is_ok = False
    else:
        queue.is_ok = True


def _reset_connection_interface(arg):
    queue.set_step(sub=0, base=7, success=8, fail=9, interval=1, is_ok=False, retry=2)

    try:
        modem.reset_connection_interface()
    except Exception as e:
        logger.error("reset_connection_interface() -> " + str(e))
        queue.is_ok = False
    else:
        queue.is_ok = True


def _reset_usb_interface(arg):
    queue.set_step(sub=0, base=9, success=10, fail=11, interval=1, is_ok=False, retry=2)

    try:
        modem.reset_usb_interface()
    except Exception as e:
        logger.error("reset_usb_interface() -> " + str(e))
        queue.is_ok = False
    else:
        queue.is_ok = True


def _reset_modem_softly(arg):
    queue.set_step(sub=0, base=11, success=1, fail=12, interval=1, is_ok=False, retry=1)

    try:
        modem.reset_modem_softly()
    except Exception as e:
        logger.error("reset_modem_softly() -> " + str(e))
        queue.is_ok = False
    else:
        queue.is_ok = True


def _reset_modem_hardly(arg):
    queue.set_step(sub=0, base=12, success=1, fail=1, interval=1, is_ok=False, retry=1)

    try:
        modem.reset_modem_hardly()
    except Exception as e:
        logger.error("reset_modem_hardly() -> " + str(e))
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
    6: _diagnose,
    7: _reset_connection_interface,
    8: _check_internet,
    9: _reset_usb_interface,
    10: _check_internet,
    11: _reset_modem_softly,
    12: _reset_modem_hardly,
    13: _diagnose,
    14: _check_sim_ready,
    15: _diagnose,
}

  
def execute_step(x, arg=None):
    steps.get(x)(arg)


def manage_connection():
    # main execution of step
    if queue.sub == 0:
        execute_step(queue.sub)
        #print("ZeroSub: ", queue.sub, " Base: ", queue.base, " Interval: ", queue.interval)
        return queue.interval

    # organiser step
    execute_step(queue.sub)
    #print("Sub: ", queue.sub, " Base: ", queue.base, " Interval: ", queue.interval)
    return NO_WAIT_INTERVAL


if __name__  == "__main__":
    
    while True:
        interval = manage_connection()
        time.sleep(interval)

        

