import requests
import logging

from chain_sight.models.models import Delegator
from chain_sight.services.database_config import Session
from chain_sight.services.database import insert_delegator


# Assuming you've already called setup_logging() in your main.py or somewhere before this
logger = logging.getLogger(__name__)

def fetch_validators(chain_config):
    validators_endpoint = f"{chain_config.api_endpoint}/cosmos/staking/v1beta1/validators"
    all_validators = []  # Initialize a list to collect all validators

    next_key = None  # Initialize the pagination key
    while True:
        params = {
            'pagination.limit': 100  # Set a reasonable limit per page
        }
        if next_key:
            params['pagination.key'] = next_key  # Include the next_key in subsequent requests

        response = requests.get(validators_endpoint, params=params)

        if response.status_code == 200:
            data = response.json()
            validators = data.get('validators', [])
            all_validators.extend(validators)
            logger.info(f"Fetched {len(validators)} validators.")

            # Check for pagination
            pagination = data.get('pagination', {})
            next_key = pagination.get('next_key')
            if not next_key:
                break  # No more pages to fetch
        else:
            logger.error(f"Failed to fetch validators. Status code: {response.status_code}")
            break  # Exit the loop if the request fails

    return all_validators


def fetch_and_store_delegators(validator_addr, chain_config):
    delegations_endpoint = f"{chain_config.api_endpoint}/cosmos/staking/v1beta1/validators/{validator_addr}/delegations"
    active_delegator_addresses = []  # Initialize an empty list to collect active delegator addresses

    next_key = None  # Initialize the pagination key
    while True:
        params = {
            'pagination.limit': 100  # Set a reasonable limit per page
        }
        if next_key:
            params['pagination.key'] = next_key  # Include the next_key in subsequent requests

        response = requests.get(delegations_endpoint, params=params)

        if response.status_code == 200:
            data = response.json()
            delegator_entries = data.get('delegation_responses', [])
            for entry in delegator_entries:
                insert_delegator(entry, validator_addr)
                # Collect the delegator_address from each entry for later cleanup
                active_delegator_addresses.append(entry['delegation']['delegator_address'])
            logger.info(f"Fetched {len(delegator_entries)} delegators for validator {validator_addr}.")

            # Check for pagination
            pagination = data.get('pagination', {})
            next_key = pagination.get('next_key')
            if not next_key:
                break  # No more pages to fetch
        else:
            logger.error(f"Failed to fetch delegators for validator {validator_addr}. Status code: {response.status_code}")
            break  # Exit the loop if the request fails

    logger.info(f"Delegators for validator {validator_addr} fetched and stored successfully.")
    cleanup_delegators(active_delegator_addresses, validator_addr)


def fetch_governance_proposals(chain_config):
    proposals_endpoint = f"{chain_config.api_endpoint}/cosmos/gov/v1beta1/proposals"
    all_proposals = []
    next_key = None
    page_number = 0  # Start from page 0

    logger.info("Starting to fetch governance proposals.")

    while True:
        params = {}
        if next_key:
            params['pagination.key'] = next_key

        logger.debug(f"Fetching page {page_number} of proposals.")
        response = requests.get(proposals_endpoint, params=params)
        if response.status_code == 200:
            data = response.json()
            proposals = data.get('proposals', [])
            all_proposals.extend(proposals)
            logger.debug(f"Fetched {len(proposals)} proposals from page {page_number}. Total proposals so far: {len(all_proposals)}")

            pagination = data.get('pagination', {})
            next_key = pagination.get('next_key')
            if not next_key:
                logger.info("No more pages to fetch. Completed fetching all proposals.")
                break  # No more pages
            else:
                page_number += 1  # Increment page number
        else:
            logger.error(f"Failed to fetch governance proposals. Status code: {response.status_code}. Response: {response.text}")
            break

    return all_proposals


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

