import logging
import os, sys

LOG_FORMAT = "%(asctime)s %(name)20s %(funcName)25s %(levelname)s   %(message)s"

def SetUpLogger(loggerName, logFile):
    """
    Custom logger for this framework.
    """
    # Accept all level of logging.
    logging.basicConfig(level=logging.DEBUG)

    logger = logging.getLogger(loggerName)

    # Set up log file handler.
    fileHandler = logging.FileHandler(logFile)

    # Format the log message.
    formatter = logging.Formatter(LOG_FORMAT)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    return logger
