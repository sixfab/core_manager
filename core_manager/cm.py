#!/usr/bin/python3

import time

from helpers.config_parser import conf
from helpers.logger import logger
from helpers.exceptions import ModemNotFound, ModemNotSupported
from helpers.queue import Queue

from modules.identify import identify_setup, identify_modem
from modules.modem import Modem

queue = Queue()
modem = Modem()

NO_WAIT_INTERVAL = 0.1
SECOND_CHECK_INTERVAL = 10

first_connection_flag = False

logger.info("Core Manager started.")


def _organizer():
    if queue.base == 0:
        queue.sub = 16
    else:
        if queue.is_ok:
            queue.sub = queue.success
            queue.is_ok = False
        else:
            if queue.counter >= queue.retry:
                queue.sub = queue.fail
                queue.clear_counter()
                queue.interval = NO_WAIT_INTERVAL
            else:
                queue.sub = queue.base
                queue.counter_tick()

                # Exception for the second chance of internet control
                if queue.base == 5:
                    queue.interval = SECOND_CHECK_INTERVAL


def _identify_modem():
    global modem
    queue.set_step(sub=0, base=16, success=1, fail=15, interval=2, is_ok=False, retry=20)

    try:
        module = identify_modem()
    except Exception as error:
        logger.error("identify_modem -> %s", error)
        queue.is_ok = False
    else:
        modem.update(module)
        queue.is_ok = True


def _identify_setup():
    global modem
    queue.set_step(sub=0, base=1, success=2, fail=15, interval=2, is_ok=False, retry=20)

    try:
        new_id = identify_setup()
    except Exception as error:
        logger.error("identify_setup -> %s", error)
        queue.is_ok = False
    else:
        if new_id != {}:
            modem.imei = new_id.get("imei", "")
            modem.iccid = new_id.get("iccid", "")
            modem.sw_version = new_id.get("sw_version", "")
        queue.is_ok = True

        if conf.debug_mode and conf.verbose_mode:
            print("")
            print("********************************************************************")
            print("[?] MODEM REPORT")
            print("-------------------------")
            attrs = vars(modem)
            print("\n".join("[+] %s : %s" % item for item in attrs.items()))
            print("********************************************************************")
            print("")


def _configure_modem():
    queue.set_step(sub=0, base=2, success=14, fail=13, interval=1, is_ok=False, retry=5)

    try:
        modem.configure_modem()
    except ModemNotSupported:
        queue.is_ok = False
    except ModemNotFound:
        queue.is_ok = False
    except Exception as error:
        logger.error("configure_modem() -> %s", error)
        queue.is_ok = False
    else:
        queue.is_ok = True


def _check_sim_ready():
    queue.set_step(sub=0, base=14, success=3, fail=13, interval=1, is_ok=False, retry=5)

    try:
        modem.check_sim_ready()
    except Exception as error:
        logger.error("check_sim_ready() -> %s", error)
        queue.is_ok = False
    else:
        queue.is_ok = True


def _check_network():
    queue.set_step(sub=0, base=3, success=4, fail=13, interval=5, is_ok=False, retry=120)

    try:
        modem.check_network()
    except Exception as error:
        logger.error("check_network() -> %s", error)
        queue.is_ok = False
    else:
        queue.is_ok = True


def _initiate_ecm():
    queue.set_step(sub=0, base=4, success=5, fail=13, interval=0.1, is_ok=False, retry=5)

    try:
        modem.initiate_ecm()
    except Exception as error:
        logger.error("initiate_ecm() -> %s", error)
        queue.is_ok = False
    else:
        queue.is_ok = True


def _check_internet():
    global first_connection_flag

    if queue.sub == 5:
        queue.set_step(
            sub=0,
            base=5,
            success=5,
            fail=6,
            interval=conf.check_internet_interval,
            is_ok=False,
            retry=1,
        )
    elif queue.sub == 8:
        queue.set_step(sub=0, base=8, success=5, fail=9, interval=10, is_ok=False, retry=0)

    elif queue.sub == 10:
        queue.set_step(sub=0, base=10, success=5, fail=11, interval=10, is_ok=False, retry=0)

    try:
        modem.check_internet()
    except Exception as error:
        logger.error("check_internet() -> %s", error)
        queue.is_ok = False
    else:

        if not first_connection_flag:
            logger.info("Internet connection is established")
            first_connection_flag = True

        if modem.incident_flag:
            modem.monitor["fixed_incident"] += 1
            modem.incident_flag = False
            logger.info("Internet connection is restored")

        queue.is_ok = True


def _diagnose():
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
    except Exception as error:
        logger.error("diagnose() -> %s", error)
        queue.is_ok = False
    else:
        queue.is_ok = True


def _reset_connection_interface():
    queue.set_step(sub=0, base=7, success=8, fail=9, interval=1, is_ok=False, retry=2)

    try:
        modem.reset_connection_interface()
    except Exception as error:
        logger.error("reset_connection_interface() -> %s", error)
        queue.is_ok = False
    else:
        queue.is_ok = True


def _reset_usb_interface():
    queue.set_step(sub=0, base=9, success=10, fail=11, interval=1, is_ok=False, retry=2)

    try:
        modem.reset_usb_interface()
    except Exception as error:
        logger.error("reset_usb_interface() -> %s", error)
        queue.is_ok = False
    else:
        queue.is_ok = True


def _reset_modem_softly():
    queue.set_step(sub=0, base=11, success=16, fail=12, interval=1, is_ok=False, retry=1)

    try:
        modem.reset_modem_softly()
    except Exception as error:
        logger.error("reset_modem_softly() -> %s", error)
        queue.is_ok = False
    else:
        queue.is_ok = True


def _reset_modem_hardly():
    queue.set_step(sub=0, base=12, success=16, fail=16, interval=1, is_ok=False, retry=1)

    try:
        modem.reset_modem_hardly()
    except Exception as error:
        logger.error("reset_modem_hardly() -> %s", error)
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
    16: _identify_modem,
}


def execute_step(step):
    steps.get(step)()


def manage_connection():
    # main execution of step
    if queue.sub == 0:
        execute_step(queue.sub)
        return queue.interval

    # organiser step
    execute_step(queue.sub)
    return NO_WAIT_INTERVAL


if __name__ == "__main__":

    while True:
        interval = manage_connection()
        time.sleep(interval)
