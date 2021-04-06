#!/usr/bin/python3

import os.path
import sys
import logging
import logging.handlers

from helpers.config_parser import conf


LOG_PATH = os.path.expanduser("~") + "/.core/logs/"
log_format = "%(asctime)s --> %(filename)-18s %(levelname)-8s %(message)s"


def update_log_debug(logger, status):
    formatter = logging.Formatter(log_format)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.set_name("debug_handler")
    
    if status is True:
        logger.addHandler(stream_handler)
    else:
        for handler in logger.handlers:
            if handler.get_name() == "debug_handler":
                logger.removeHandler(handler)


def initialize_logger():
    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)

    logger = logging.getLogger("core_manager")
    
    if conf.logger_level == "debug":
        logger.setLevel(logging.DEBUG)
    elif conf.logger_level == "info":
        logger.setLevel(logging.INFO)
    elif conf.logger_level == "warning":
        logger.setLevel(logging.WARNING)
    elif conf.logger_level == "error":
        logger.setLevel(logging.ERROR)
    elif conf.logger_level == "critical":
        logger.setLevel(logging.CRITICAL)

    formatter = logging.Formatter(log_format)
    log_file_handler = logging.handlers.RotatingFileHandler(
                                                            filename=LOG_PATH+"cm-log", 
                                                            maxBytes=10*1024*1024,
                                                            backupCount=3
    )
    
    log_file_handler.setFormatter(formatter)
    log_file_handler.set_name("log_handler")

    logger.addHandler(log_file_handler)

    if conf.debug_mode:
        update_log_debug(logger, True)

    return logger


logger = initialize_logger()