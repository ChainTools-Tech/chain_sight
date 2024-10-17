import json
import logging

from chain_sight.services.database_config import Session
from chain_sight.models.models import ChainConfig


logger = logging.getLogger(__name__)


def load_config(chain_name=None):
    """Load chain configuration from the database. Optionally, filter by chain name."""
    session = Session()
    try:
        if chain_name:
            # Query for the specified chain
            chain_config = session.query(ChainConfig).filter(ChainConfig.chain_id == chain_name).first()
            logger.debug(f'Loaded {chain_name} chain details: {chain_config}')
            return chain_config
        else:
            # Return all chain configurations
            chain_configs = session.query(ChainConfig).all()
            logger.debug(f'Loaded chains information: {chain_configs}')
            return chain_configs
    finally:
        session.close()
