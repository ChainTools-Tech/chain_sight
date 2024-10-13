import logging
import sys


def get_log_level(level_str):
    try:
        return getattr(logging, level_str.upper())
    except AttributeError:
        return logging.INFO


def setup_logging(log_file, log_level=logging.INFO):
    log_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)-8s] %(name)s: (%(module)s, %(funcName)s): %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove all existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Configure file handler
    file_handler = logging.FileHandler(filename=log_file, encoding='utf-8', mode='w')
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)


# Old logger

# def setup_logging():
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     # Create a logger object
#     logger = logging.getLogger('ChainSight')
#     logger.setLevel(logging.DEBUG)  # Set the minimum level of messages to log
#
#     # Create a file handler that logs debug and higher level messages
#     file_handler = RotatingFileHandler('chainsight.log', maxBytes=1024*1024*5, backupCount=5)
#     file_handler.setLevel(logging.DEBUG)
#     file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     file_handler.setFormatter(file_formatter)
#     logger.addHandler(file_handler)
#
#     # Create console handler with a higher log level
#     console_handler = logging.StreamHandler()
#     console_handler.setLevel(logging.INFO)
#     console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
#     console_handler.setFormatter(console_formatter)
#     logger.addHandler(console_handler)
#
#     return logger