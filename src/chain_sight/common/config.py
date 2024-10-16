import json
import logging

from chain_sight.services.database_config import Session
from chain_sight.models.models import ChainConfig


logger = logging.getLogger(__name__)


def load_config(chain_name=None):
    """Load chain configuration from the database. Optionally, filter by chain name."""
    session = Session()
    chain_configs = session.query(ChainConfig.name).all()
    logger.debug(f'Initial read of all chains: {chain_configs}')
    logger.debug(f"Retrieved {len(chain_configs)} entries from the ChainConfig table:")
    for config in chain_configs:
        logger.debug(config)
    try:
        if chain_name:
            # Query for the specified chain
            chain_config = session.query(ChainConfig).filter(ChainConfig.name == chain_name).first()
            logger.debug(f'Loaded {chain_name} chain details: {chain_config}')
            return chain_config
        else:
            # Return all chain configurations
            chain_configs = session.query(ChainConfig).all()
            logger.debug(f'Loaded chains information: {chain_configs}')
            return chain_configs
    finally:
        session.close()


def load_config_file(chain_name=None):
    """Load chain configuration. Optionally, filter by chain name."""
    with open('config/chains.json', 'r') as f:
        config = json.load(f)
    if chain_name:
        # Filter for the specified chain
        chain_config = next((item for item in config["chains"] if item["name"] == chain_name), None)
        return chain_config
    return config


