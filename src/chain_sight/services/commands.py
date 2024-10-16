import json
import logging
import os

from chain_sight.common.config import load_config
from chain_sight.models.models import ChainConfig
from chain_sight.services.blockchain import fetch_validators, fetch_and_store_delegators, fetch_governance_proposals
from chain_sight.services.database_config import Session
from chain_sight.services.database import insert_validator, insert_or_update_governance_proposal


logger = logging.getLogger(__name__)


def config_import(config_path):
    """
    Imports chain configurations from a JSON file into the database.
    If a chain exists but has different parameters, updates the database record.

    Args:
        config_path (str): The file path to the configuration JSON file.
    """
    if not os.path.isfile(config_path):
        logger.error(f"The configuration file does not exist at the specified path: {config_path}")
        return

    try:
        with open(config_path, 'r') as file:
            config_data = json.load(file)
    except json.JSONDecodeError as jde:
        logger.error(f"JSON decode error while reading the configuration file: {jde}")
        return
    except Exception as e:
        logger.error(f"An unexpected error occurred while reading the configuration file: {e}")
        return

    session = Session()

    try:
        for chain in config_data.get('chains', []):
            # Validate required fields
            required_fields = ['name', 'chain_id', 'prefix', 'rpc_endpoint', 'api_endpoint']
            if not all(field in chain for field in required_fields):
                logger.warning(f"Skipping chain due to missing required fields: {chain}")
                continue

            # Check if the chain configuration already exists based on 'chain_id'
            existing_chain = session.query(ChainConfig).filter(
                ChainConfig.chain_id == chain['chain_id']
            ).first()

            if not existing_chain:
                # If it doesn't exist, create a new ChainConfig object and add it to the session
                new_chain = ChainConfig(
                    name=chain['name'],
                    chain_id=chain['chain_id'],
                    prefix=chain['prefix'],
                    rpc_endpoint=chain['rpc_endpoint'],
                    api_endpoint=chain['api_endpoint'],
                    grpc_endpoint=chain.get('grpc_endpoint')  # Use .get() to handle optional fields
                )
                session.add(new_chain)
                logger.info(f"Added new chain configuration: {chain['name']}")
            else:
                # Compare each field to detect changes
                updated = False
                fields_to_compare = ['name', 'prefix', 'rpc_endpoint', 'api_endpoint', 'grpc_endpoint']

                for field in fields_to_compare:
                    config_value = chain.get(field)
                    db_value = getattr(existing_chain, field)

                    # Handle None values for optional fields like 'grpc_endpoint'
                    if config_value != db_value:
                        setattr(existing_chain, field, config_value)
                        updated = True
                        logger.debug(f"Updated '{field}' for chain '{existing_chain.name}' from '{db_value}' to '{config_value}'")

                if updated:
                    logger.info(f"Updated chain configuration: {existing_chain.name}")
                else:
                    logger.info(f"No changes detected for chain: {existing_chain.name}")

        # Commit the session to save changes to the database
        session.commit()
        logger.info("Configurations imported successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"An error occurred during configuration import: {e}")
    finally:
        session.close()


# def config_display():
#     config = load_config()
#     print(json.dumps(config, indent=4))

def config_display():
    """
    Retrieves chain configurations from the database and displays them in JSON format.
    The output mirrors the structure of the original configuration JSON file.
    """
    session = Session()
    try:
        chains = session.query(ChainConfig).all()
        if not chains:
            logger.info("No chain configurations found in the database.")
            print(json.dumps({"chains": []}, indent=4))
            return

        config = {"chains": []}
        for chain in chains:
            chain_dict = {
                "name": chain.name,
                "chain_id": chain.chain_id,
                "prefix": chain.prefix,
                "rpc_endpoint": chain.rpc_endpoint,
                "api_endpoint": chain.api_endpoint,
                "grpc_endpoint": chain.grpc_endpoint  # This may be None if not set
            }
            config["chains"].append(chain_dict)

        # Output the configuration in JSON format
        print(json.dumps(config, indent=4))
    except Exception as e:
        logger.error(f"An error occurred while displaying configurations: {e}")
    finally:
        session.close()


def fetch_and_store_validators(chain_name):
    chain_config = load_config(chain_name)
    if not chain_config:
        logger.error(f"No configuration found for chain: {chain_name}")
        return

    validators = fetch_validators(chain_config)
    if validators:
        for validator in validators:
            # Insert each validator into the database
            insert_validator(validator, chain_config.chain_id)
            # After inserting a validator, fetch and store its delegators
            fetch_and_store_delegators(validator['operator_address'], chain_config)
        logger.info(f"Validators and their delegators for {chain_name} fetched and stored successfully.")
    else:
        logger.warning(f"No validators found for {chain_name}.")


def fetch_and_store_governance_proposals(chain_name):
    chain_config = load_config(chain_name)
    if not chain_config:
        logger.error(f"No configuration found for chain: {chain_name}")
        return

    chain_id = chain_config.chain_id  # Access chain_id attribute

    proposals = fetch_governance_proposals(chain_config)
    if proposals:
        for proposal in proposals:
            title = proposal.get("title")
            logger.info(f"Proposal '{proposal_id}' has 'title' {title}")
            insert_or_update_governance_proposal(proposal, chain_id)
        logger.info(f"Governance proposals for {chain_name} fetched and stored successfully.")
    else:
        logger.warning(f"No governance proposals found for {chain_name}.")