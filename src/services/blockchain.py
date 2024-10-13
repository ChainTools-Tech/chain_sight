import requests
import logging

from src import Delegator, Session
from src import insert_delegator


# Assuming you've already called setup_logging() in your main.py or somewhere before this
logger = logging.getLogger(__name__)

def fetch_validators(chain_config):
    validators_endpoint = f"{chain_config['api_endpoint']}/cosmos/staking/v1beta1/validators?pagination.count_total=true"
    response = requests.get(validators_endpoint)
    if response.status_code == 200:
        return response.json()['validators']
    else:
        logger.error("Failed to fetch validators.")
        return []


def fetch_and_store_delegators(validator_addr, chain_config):
    delegations_endpoint = f"{chain_config['api_endpoint']}/cosmos/staking/v1beta1/validators/{validator_addr}/delegations?pagination.count_total=true"
    response = requests.get(delegations_endpoint)
    active_delegator_addresses = []  # Initialize an empty list to collect active delegator addresses

    if response.status_code == 200:
        delegator_entries = response.json().get('delegation_responses', [])
        for entry in delegator_entries:
            insert_delegator(entry, validator_addr)
            # Collect the delegator_address from each entry for later cleanup
            active_delegator_addresses.append(entry['delegation']['delegator_address'])
        logger.info(f"Delegators for validator {validator_addr} fetched and stored successfully.")
        cleanup_delegators(active_delegator_addresses, validator_addr)
    else:
        logger.error(f"Failed to fetch delegators for validator {validator_addr}.")


def fetch_governance_proposals(chain_config):
    proposals_endpoint = f"{chain_config['api_endpoint']}/cosmos/gov/v1beta1/proposals"
    response = requests.get(proposals_endpoint)
    if response.status_code == 200:
        return response.json().get('proposals', [])
    else:
        logger.error("Failed to fetch governance proposals.")
        return []


def cleanup_delegators(active_delegators, validator_address):
    session = Session()
    try:
        all_delegators = session.query(Delegator).filter_by(validator_address=validator_address).all()
        inactive_delegators = [d for d in all_delegators if d.delegator_address not in active_delegators]

        for delegator in inactive_delegators:
            # Example for flagging as inactive
            delegator.active = False
            logger.info(f"Flagging delegator {delegator.delegator_address} of validator {validator_address} as inactive.")
            # If deleting, uncomment the next line
            logger.info(f"Removing delegator {delegator.delegator_address} of validator {validator_address} from database.")
            session.delete(delegator)

        session.commit()
    except Exception as e:
        logger.error(f"An error occurred during cleanup: {e}")
        session.rollback()
    finally:
        session.close()

