import os
import sys
import logging
import logging.handlers

logger = None

def initialize_logger(debug=False):
    global logger
    if logger:
        return logger

    logging_file_path = os.path.expanduser("~")+"/.sixfab/connect/"
    
    if not os.path.exists(logging_file_path):
        os.mkdir(logging_file_path)

    logger = logging.getLogger("connection_manager")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
    log_file_handler = logging.handlers.RotatingFileHandler(
                                                            filename=logging_file_path+"cm-log", 
                                                            maxBytes=10*1024*1024,
                                                            backupCount=3
                                                            )
    if debug is True:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    log_file_handler.setFormatter(formatter)

    logger.addHandler(log_file_handler)

    return logger