import logging
import sys

import chain_sight.services.commands

from chain_sight.common.cli import parse_args
from chain_sight.common.logger import get_log_level, setup_logging
from chain_sight.services.database_config import initialize_database
from chain_sight.services.commands import config_display, config_import


def main():
    args = parse_args()

    initialize_database()

    log_level = get_log_level(args.log_level)
    setup_logging(log_file=args.log_file, log_level=log_level)

    logger = logging.getLogger(__name__)
    logger.debug("Application started with arguments: %s", args)

    if args.config:
        logger.debug(f'Configuration mode selected: {args.config}')
        if args.config == 'import':
            logger.debug(f'Configuration file path provided: {args.config_path}')
            config_import(args.config_path)
        elif args.config == 'display':
            config_display()
    elif args.fetch:
        logger.debug(f'Fetch mode selected: {args.fetch}')
        logger.debug(f'Chain specified: {args.chain}')
        if args.fetch == 'governance':
            try:
                chain_sight.services.commands.fetch_and_store_governance_proposals(args.chain)
                logger.info("Governance proposals fetched and stored successfully.")
            except Exception as e:
                logger.error(f"Failed to fetch and store governance proposals: {e}")
        elif args.fetch == 'validators':
            try:
                chain_sight.services.commands.fetch_and_store_validators(args.chain)
                logger.info("Validators fetched and stored successfully.")
            except Exception as e:
                logger.error(f"Failed to fetch and store validators: {e}")
    else:
        logger.error("No valid operation specified. Use --help for usage information.")
        sys.exit(1)

if __name__ == '__main__':
    main()
