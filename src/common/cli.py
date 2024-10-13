import argparse
import logging


logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(prog='chain_sight',
                                     description='CLI tool for configuration and data fetching.',
                                     epilog='... and data will go to database')
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # config-import command
    parser_config_import = subparsers.add_parser('config-import',
                                                 help='Import a configuration file.')
    parser_config_import.add_argument('config_file_path',
                                      type=str,
                                      action='store',
                                      default='config/chains.json',
                                      help='Path to the configuration file (default: config/chains.json).')

    # fetch-and-store-validators command
    parser_fetch_validators = subparsers.add_parser('fetch-and-store-validators',
                                                    help='Fetch and store validators data.')
    parser_fetch_validators.add_argument('chain_name',
                                         type=str,
                                         action='store',
                                         help='Name of the blockchain chain.')

    # fetch-and-store-governance-proposals command
    parser_fetch_governance = subparsers.add_parser('fetch-and-store-governance-proposals',
                                                    help='Fetch and store governance proposals.')
    parser_fetch_governance.add_argument('chain_name',
                                         type=str,
                                         action='store',
                                         help='Name of the blockchain chain.')

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

    return parser.parse_args()
