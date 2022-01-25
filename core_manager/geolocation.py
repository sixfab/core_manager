import time
import os.path

from helpers.config_parser import conf
from helpers.logger import logger
from helpers.yamlio import read_yaml_all, write_yaml_all, GEOLOCATION_PATH


def update_geolocation(modem):
    geolocation_data = {}
    old_geolocation = {}

    if os.path.isfile(GEOLOCATION_PATH):
        try:
            old_geolocation = read_yaml_all(GEOLOCATION_PATH)
        except:
            logger.warning("Old geolocation data in geolocation.yaml file couln't be read!")

    geolocation_data["last_update"] = old_geolocation.get("last_update", int(time.time()))

    try:
        modem.read_geoloc_data()
    except:
        logger.error("Error occured getting geolocation data")
    else:
        geolocation_data = modem.geolocation


    if geolocation_data != old_geolocation:

        geolocation_data["last_update"] = int(time.time())

        # Save ID's to file
        try:
            write_yaml_all(GEOLOCATION_PATH, geolocation_data)
        except Exception as error:
            logger.error("write_yaml_all(GEOLOCATION_PATH, geolocation_data) -> %s", error)
        else:
            logger.info("Geolocation data updated with changes.")

            # GEOLOCATION REPORT
            if conf.debug_mode and conf.verbose_mode:
                print("")
                print("********************************************************************")
                print("[?] GEOLOCATION REPORT")
                print("-------------------------")
                for item in geolocation_data.items():
                    print(f"[+] {item[0]} --> {item[1]}")
                print("********************************************************************")
                print("")
            # END OF GEOLOCATION REPORT
    else:
        # logger.debug("No change on geolocation data.")
        pass
