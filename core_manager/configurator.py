import os
import glob
import time

from helpers.yamlio import read_yaml_all, write_yaml_all, CONFIG_FOLDER_PATH, CONFIG_PATH
from helpers.config_parser import logger, get_configs
from helpers.commander import shell_command

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
            conf = get_configs()
            conf.reload_required = True
            logger.info("New configs are applied.")


def configure():

    get_requests()

    for i in range(len(waiting_requests)):
        save_configuration()
        print("Actual Config: ", actual_configs)
        print("Waiting Requests Count: ", len(waiting_requests))
        print("Processing Requests Count: ", len(processing_requests))
        print("\n")

    apply_configs()



if __name__ == "__main__":
    while True:
        conf = get_configs()
        
        attrs = vars(conf)
        print(', '.join("%s: %s" % item for item in attrs.items()))
        print("---------------------------------------------------------")
        
        configure()