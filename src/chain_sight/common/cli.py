import argparse
import logging
import sys

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        prog='chain_sight',
        description='CLI tool for configuration and data fetching.',
        epilog='... and data will go to database'
    )

    group = parser.add_mutually_exclusive_group(required=True)

    # --config option with choices 'import' and 'display'
    group.add_argument(
        '--config',
        type=str,
        choices=['import', 'display'],
        help='Use configuration mode: "import" to import configurations, "display" to display configurations.'
    )

    # --fetch option with choices 'validators' and 'governance'
    group.add_argument(
        '--fetch',
        type=str,
        choices=['validators', 'governance'],
        help='Use fetch mode: "validators" to fetch validator data, "governance" to fetch governance proposals.'
    )

    # --config-path argument, required only when --config is 'import'
    parser.add_argument(
        '--config-path',
        type=str,
        help='Path to the configuration file (required when --config is "import").'
    )

    parser.add_argument(
        '--chain',
        type=str,
        help='Specify the chain (required if --fetch is used).'
    )

    parser.add_argument(
        '--log-file',
        type=str,
        default='chain_sight.log',
        help='Set the log file path. Defaults to "chain_sight.log".'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the logging level. Defaults to "INFO".'
    )

    args = parser.parse_args()

    # Perform conditional checks here
    if args.fetch and not args.chain:
        parser.error("argument --chain is required when --fetch is specified")

    if args.config:
        if args.config == 'import' and not args.config_path:
            parser.error("argument --config-path is required when --config is 'import'")
        if args.config != 'import' and args.config_path:
            parser.error("argument --config-path should only be used with --config 'import'")

    return args


def setup_logging(log_file, log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        print(f"Invalid log level: {log_level}")
        sys.exit(1)

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


if __name__ == "__main__":
    args = parse_args()
    setup_logging(args.log_file, args.log_level)
    logger.info("Application started with arguments: %s", args)
    # Here you would import and call the relevant functions based on args
