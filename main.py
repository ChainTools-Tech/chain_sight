import logging
from logging.handlers import RotatingFileHandler
from src.cli.commands import cli
from src.services.database_config import initialize_database

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Create a logger object
    logger = logging.getLogger('ChainSight')
    logger.setLevel(logging.DEBUG)  # Set the minimum level of messages to log

    # Create a file handler that logs debug and higher level messages
    file_handler = RotatingFileHandler('chainsight.log', maxBytes=1024*1024*5, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Create console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


def main():
    initialize_database()
    setup_logging()
    cli()


if __name__ == '__main__':
    main()
