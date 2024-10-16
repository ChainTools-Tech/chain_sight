import logging

import chain_sight.services.commands

from chain_sight.common.cli import parse_args
from chain_sight.common.logger import get_log_level, setup_logging
from chain_sight.services.database_config import initialize_database
from chain_sight.services.commands import config_display, config_import



logger = logging.getLogger(__name__)


def main():
    args = parse_args()

    initialize_database()

    log_level = get_log_level(args.log_level)
    setup_logging(log_file=args.log_file, log_level=log_level)

    if args.config:
        logger.debug(f'Configuration mode selected: {args.config}')
        if args.config == 'import':
            config_import()
        elif args.config == 'display':
            config_display()
    elif args.fetch:
        logger.debug(f'Fetch mode selected: {args.fetch}')
        logger.debug(f'Chain specified: {args.chain}')
        if args.fetch == 'governance':
            chain_sight.services.commands.fetch_and_store_governance_proposals(args.chain)
        elif args.fetch == 'validators':
            chain_sight.services.commands.fetch_and_store_validators(args.chain)

if __name__ == '__main__':
    main()
