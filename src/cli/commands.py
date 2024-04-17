import json
import os

import click
import logging

from src.models.models import ChainConfig
from src.services.blockchain import fetch_validators, fetch_and_store_delegators, fetch_governance_proposals
from src.services.database import insert_validator, insert_or_update_governance_proposal
from src.services.database_config import Session
from src.common.utils import load_config


# Setup logger for this module
logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@click.command(name='config-import')
def config_import():
    """Import chain configurations from config.json into the database."""
    # Path to your config.json file
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    config_path = os.path.join(base_dir, 'config', 'chains.json')  # Correct file name and path

    # Read the configuration file
    with open(config_path, 'r') as file:
        config_data = json.load(file)

    # Create a new database session
    session = Session()

    try:
        for chain in config_data['chains']:
            # Check if the chain configuration already exists to avoid duplication
            exists = session.query(ChainConfig).filter(
                (ChainConfig.name == chain['name']) |
                (ChainConfig.chain_id == chain['chain_id'])
            ).first()

            if not exists:
                # If it doesn't exist, create a new ChainConfig object and add it to the session
                new_chain = ChainConfig(
                    name=chain['name'],
                    chain_id=chain['chain_id'],
                    prefix=chain['prefix'],
                    rpc_endpoint=chain['rpc_endpoint'],
                    api_endpoint=chain['api_endpoint'],
                    grpc_endpoint=chain['grpc_endpoint']
                )
                session.add(new_chain)
                click.echo(f"Added new chain configuration: {chain['name']}")

        # Commit the session to save changes to the database
        session.commit()
        click.echo("Configurations imported successfully.")
    except Exception as e:
        session.rollback()
        click.echo(f"An error occurred: {e}")
    finally:
        session.close()


@click.command()
@click.argument('chain_name')
def fetch_and_store_validators(chain_name):
    # Load the specific chain configuration
    chain_config = load_config(chain_name)
    if not chain_config:
        logger.error(f"No configuration found for chain: {chain_name}")
        return

    # Fetch validators using the loaded chain configuration
    validators = fetch_validators(chain_config)
    if validators:
        for validator in validators:
            # Insert each validator into the database
            # Ensure chain_id is passed to insert_validator
            insert_validator(validator, chain_config['chain_id'])  # Pass chain_id explicitly
            # After inserting a validator, fetch and store its delegators
            fetch_and_store_delegators(validator['operator_address'], chain_config)
        logger.info(f"Validators and their delegators for {chain_name} fetched and stored successfully.")
    else:
        logger.warning(f"No validators found for {chain_name}.")


@click.command()
@click.argument('chain_name')
def fetch_and_store_governance_proposals(chain_name):
    chain_config = load_config(chain_name)
    if not chain_config:
        logger.error(f"No configuration found for chain: {chain_name}")
        return

    chain_id = chain_config["chain_id"]  # Extract the chain ID from the configuration

    proposals = fetch_governance_proposals(chain_config)
    if proposals:
        for proposal in proposals:
            insert_or_update_governance_proposal(proposal, chain_id)  # Pass chain_id here
        logger.info(f"Governance proposals for {chain_name} fetched and stored successfully.")
    else:
        logger.warning(f"No governance proposals found for {chain_name}.")


cli.add_command(fetch_and_store_validators)
cli.add_command(fetch_and_store_governance_proposals)
cli.add_command(config_import)