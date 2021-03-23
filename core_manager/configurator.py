import os.path
import glob

from helpers.yamlio import read_yaml_all, write_yaml_all, CONFIG_FOLDER_PATH, CONFIG_PATH
from helpers.config_parser import logger, config

CONFIG_REQUEST_PATH = CONFIG_FOLDER_PATH + "request"


waiting_requests = []
processing_requests = []


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
        actual_keys = set(config.keys())
        shared_keys = request_keys.intersection(actual_keys)
        added = request_keys - actual_keys
        modified = {x : (request[x], config[x]) for x in shared_keys if request[x] != config[x]}
        
        diff = {}
        
        for key in added:
            diff[key] = request[key]

        for key in modified:
            diff[key] = request[key]
            
        return diff


def save_configuration():
    num_of_req = len(waiting_requests)
    
    if num_of_req:
        req = waiting_requests[-1] 
        try:
            diff = compare_request(req)
            print(diff)
        except Exception as e:
            logger.error("compare_request() --> " + str(e))
        else:
            for x in diff:
                config[x] = diff[x]
            
            try:
                write_yaml_all(CONFIG_PATH, config)
            except Exception as e:
                logger.error("save_configuration --> " + str(e))
            else:    
                waiting_requests.pop()


def configure():

    # Read requests and add queue
    get_requests()
    print(waiting_requests)
    print("\n")

    save_configuration()
    print("Actual Config:", config)
    print("\n")

    save_configuration()
    print("Actual Config:", config)
    print("\n")

    save_configuration()
    print("Actual Config:", config)
    print("\n")

    save_configuration()
    print("Actual Config:", config)
    print("\n")

 
    # Compare request in queue with actual config
    # If there is a difference update config file 
    # Apply it if there are new configs 
    # After applying rename request file with done or failed


if __name__ == "__main__":
    configure()