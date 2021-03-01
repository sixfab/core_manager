#!/usr/bin/python3

import os
import sys
import logging
import logging.handlers

logger = None

def initialize_logger(debug=False):
    global logger
    if logger:
        return logger

    LOG_PATH = os.path.expanduser("~")+"/.core/logs/"
    
    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)

    logger = logging.getLogger("core_manager")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s --> %(filename)-14s %(levelname)-8s %(message)s")
    log_file_handler = logging.handlers.RotatingFileHandler(
                                                            filename=LOG_PATH+"cm-log", 
                                                            maxBytes=10*1024*1024,
                                                            backupCount=3
    )
    
    if debug == True:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    log_file_handler.setFormatter(formatter)

    logger.addHandler(log_file_handler)

    return logger