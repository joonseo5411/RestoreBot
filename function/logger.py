import logging
import os
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
formatter.datefmt = '%m-%d-%Y %I:%M:%S %p'


def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

logger = setup_logger(__name__, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'logs', 'bot.log')))
usrlogger = setup_logger("UserVerify", os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'logs', 'verify.log')))