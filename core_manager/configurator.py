import os
import glob
import time

from helpers.yamlio import read_yaml_all, write_yaml_all, CONFIG_FOLDER_PATH, CONFIG_PATH
from helpers.config_parser import logger, conf, get_configs
from helpers.commander import shell_command

from cm import queue

CONFIG_REQUEST_PATH = CONFIG_FOLDER_PATH + "request"

waiting_requests = []
processing_requests = []
actual_configs = {}

def get_actual_configs():
    if os.path.isfile(CONFIG_PATH):
        try:
            actual_configs = read_yaml_all(CONFIG_PATH)
        except Exception as e:
            raise RuntimeError("get_actual_configs() -->" + str(e))
        else:
            return actual_configs
    else:
        logger.info("Config file doesn't exist!")


def get_requests():
    for file in sorted(glob.glob(CONFIG_REQUEST_PATH + "/config_request*.yaml"), reverse=True):
        waiting_requests.append(file)


def compare_request(request_file):
    try:
        request = read_yaml_all(request_file).get("configs", "")
    except Exception as e:
        raise RuntimeError(e)
    else:
        request_keys = set(request.keys())
        actual_keys = set(actual_configs.keys())
        shared_keys = request_keys.intersection(actual_keys)
        added = request_keys - actual_keys
        modified = {x : (request[x], actual_configs[x]) for x in shared_keys if request[x] != actual_configs[x]}
        
        diff = {}
        
        for key in added:
            diff[key] = request[key]

        for key in modified:
            diff[key] = request[key]
            
        return diff


def save_configuration():
    num_of_req = len(waiting_requests)
    
    try:
        get_actual_configs()
    except Exception as e:
        logger.error(str(e))
        return

    if num_of_req:
        req = waiting_requests[-1] 
        try:
            diff = compare_request(req)
            print(diff)
        except Exception as e:
            logger.error("compare_request() --> " + str(e))
        else:
            for x in diff:
                actual_configs[x] = diff[x]
            
            try:
                write_yaml_all(CONFIG_PATH, actual_configs)
            except Exception as e:
                logger.error("save_configuration --> " + str(e))
            else:    
                waiting_requests.pop()
                processing_requests.append(req)


def apply_configs():

    if len(processing_requests):
        try:
            for x in processing_requests:
                filename = os.path.basename(x)
                done = filename + "_done"

                old = os.path.join(CONFIG_REQUEST_PATH, filename)
                new = os.path.join(CONFIG_REQUEST_PATH, done)         
                os.rename(old, new)
            
                print(done)
        except Exception as e:
            logger.error("apply_configs() --> " + str(e))
        else:
            processing_requests.clear()
            conf.reload_required = True
            logger.info("New configs are applied.")


def config_report(): 
    if conf.debug_mode == True and conf.verbose_mode == True:
        print("")
        print("********************************************************************")
        print("[?] CONFIG REPORT")
        print("-------------------------")
        attrs = vars(conf)
        print('\n'.join("[+] %s --> %s" % item for item in attrs.items()))
        print("")
        print("********************************************************************")


def configure():

    get_requests()

    for i in range(len(waiting_requests)):
        save_configuration()
        print("Actual Config: ", actual_configs)
        #print("Waiting Requests Count: ", len(waiting_requests))
        #print("Processing Requests Count: ", len(processing_requests))
        #print("\n")

    apply_configs()

    if conf.reload_required:
        print("Reload is required")
        try: 
            conf.update_config(get_configs())
        except Exception as e:
            logger.error("conf.update_config() -->" + str(e))
        else:
            print("Reloaded")
            conf.reload_required = False

    if conf.is_config_changed():
        print("Config is changed. Go to identification step!")
        queue.set_step(sub=0, base=1, success=2, fail=13, interval=0.1, is_ok=False, retry=50)
        conf.config_changed = False

    config_report()

  
if __name__ == "__main__":
    while True:
        config_report()
        
        configure()
        time.sleep(5)