import argparse
import logging


logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(prog='chain_sight',
                                     description='CLI tool for configuration and data fetching.',
                                     epilog='... and data will go to database')
    group = parser.add_mutually_exclusive_group(required=True)

    # config-import command
    group.add_argument('--config',
                       type=str,
                       action='store',
                       choices=['import', 'display'],
                       help='Use configuration mode')
    group.add_argument('--fetch',
                       type=str,
                       action='store',
                       choices=['validators', 'governance'],
                       help='Use fetch mode')
    parser.add_argument('--chain',
                        type=str,
                        action='store',
                        help='Specify the chain (required if --fetch is used)')
    parser.add_argument('--log-file',
                        action='store',
                        dest='log_file',
                        default='chain_sight.log',
                        help='Set the log file path')
    parser.add_argument('--log-level',
                        action='store',
                        dest='log_level',
                        default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level.')

    args = parser.parse_args()

    # Perform conditional checks here
    if args.fetch and not args.chain:
        parser.error("argument --chain is required when --fetch is specified")
    if args.config and args.chain:
        parser.error("argument --chain is not allowed with --config")

    return args
