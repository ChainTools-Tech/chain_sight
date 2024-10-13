import logging

from common.cli import parse_args
from common.config import load_config
from common.logger import get_log_level, setup_logging
from services.commands import config_import, fetch_and_store_governance_proposals, fetch_and_store_validators
from services.database_config import initialize_database



logger = logging.getLogger(__name__)


def main():
    args = parse_args()

    initialize_database()

    log_level = get_log_level(args.log_level)
    setup_logging(log_file='chainsight.log', log_level=log_level)

    if args.command == 'config-import':
        config_import()
    elif args.command == 'fetch-and-store-validators':
        fetch_and_store_validators(args.chain_name)
    elif args.command == 'fetch-and-store-governance-proposals':
        fetch_and_store_governance_proposals(args.chain_name)


if __name__ == '__main__':
    main()
