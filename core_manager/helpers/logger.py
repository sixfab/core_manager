#!/usr/bin/python3

import os.path
import sys
import logging
import logging.handlers

from helpers.config_parser import conf


LOG_PATH = os.path.expanduser("~") + "/.core/logs/"
LOG_FORMAT = "%(asctime)s --> %(filename)-18s %(levelname)-8s %(message)s"


def update_log_debug(logger_object, status):
    formatter = logging.Formatter(LOG_FORMAT)
    debug_handler = logging.StreamHandler(sys.stdout)
    debug_handler.setFormatter(formatter)
    debug_handler.set_name("debug_handler")

    if status is True:
        logger_object.addHandler(debug_handler)
    else:
        for handler in logger_object.handlers:
            if handler.get_name() == "debug_handler":
                logger_object.removeHandler(handler)


def initialize_logger():
    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)

    logger_object = logging.getLogger("core_manager")

    if conf.logger_level == "debug":
        logger_object.setLevel(logging.DEBUG)
    elif conf.logger_level == "info":
        logger_object.setLevel(logging.INFO)
    elif conf.logger_level == "warning":
        logger_object.setLevel(logging.WARNING)
    elif conf.logger_level == "error":
        logger_object.setLevel(logging.ERROR)
    elif conf.logger_level == "critical":
        logger_object.setLevel(logging.CRITICAL)

    formatter = logging.Formatter(LOG_FORMAT)
    log_file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=LOG_PATH+"cm-log", when="midnight", backupCount=6
    )

    # log handler (root)
    log_file_handler.setFormatter(formatter)
    log_file_handler.set_name("log_handler")
    logger_object.addHandler(log_file_handler)

    if conf.debug_mode:
        # debug handler (stream)
        update_log_debug(logger_object, True)

    return logger_object


logger = initialize_logger()
