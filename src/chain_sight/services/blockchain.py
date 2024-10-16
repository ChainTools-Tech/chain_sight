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

    logger.debug(f'Fetching validators data from {validators_endpoint}.')

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
    logger.debug(f'Fetching delegators data from {delegations_endpoint}.')
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
    """
    Fetches governance proposals from the specified blockchain network.
    Attempts to use the newer '/v1/proposals' endpoint first.
    Falls back to '/v1beta1/proposals' if '/v1/proposals' is unavailable.

    Args:
        chain_config (ChainConfig): The chain configuration object containing API endpoints.

    Returns:
        list: A list of governance proposals fetched from the API.
    """
    # Define both endpoints, preferring the newer one
    endpoints = [
        f"{chain_config.api_endpoint}/cosmos/gov/v1/proposals",
        f"{chain_config.api_endpoint}/cosmos/gov/v1beta1/proposals"
    ]

    all_proposals = []
    next_key = None
    page_number = 0  # Start from page 0
    selected_endpoint = None  # To keep track of which endpoint is being used

    for endpoint in endpoints:
        logger.debug(f"Attempting to fetch governance proposals from {endpoint}.")
        try:
            # Initial request to check if the endpoint is available
            response = requests.get(endpoint, params={'pagination.limit': 1})
            if response.status_code == 200:
                selected_endpoint = endpoint
                logger.info(f"Using governance proposals endpoint: {selected_endpoint}")
                break  # Exit the loop if the endpoint is available
            else:
                logger.warning(
                    f"Endpoint {endpoint} returned status code {response.status_code}. Trying next endpoint.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to {endpoint}: {e}. Trying next endpoint.")

    if not selected_endpoint:
        logger.error("Neither '/v1/proposals' nor '/v1beta1/proposals' endpoints are available.")
        return all_proposals  # Return empty list or consider raising an exception

    # Start fetching proposals from the selected endpoint
    proposals_endpoint = selected_endpoint

    while True:
        params = {
            'pagination.limit': 100  # Adjust the limit as needed for efficiency
        }
        if next_key:
            params['pagination.key'] = next_key

        logger.info(f"Fetching page {page_number} of proposals from {proposals_endpoint}.")
        try:
            response = requests.get(proposals_endpoint, params=params)
            if response.status_code == 200:
                data = response.json()
                proposals = data.get('proposals', [])
                all_proposals.extend(proposals)
                logger.debug(
                    f"Fetched {len(proposals)} proposals from page {page_number}. Total proposals so far: {len(all_proposals)}")

                pagination = data.get('pagination', {})
                next_key = pagination.get('next_key')
                if not next_key:
                    logger.info("No more pages to fetch. Completed fetching all proposals.")
                    break  # No more pages
                else:
                    page_number += 1  # Increment page number
            else:
                logger.error(
                    f"Failed to fetch governance proposals. Status code: {response.status_code}. Response: {response.text}")
                break  # Exit loop on failure
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception occurred: {e}. Stopping fetch operation.")
            break  # Exit loop on exception

    return all_proposals


def cleanup_delegators(active_delegators, validator_address):
    session = Session()

    logger.debug(f'Delegators cleanup process starting.')

    try:
        all_delegators = session.query(Delegator).filter_by(validator_address=validator_address).all()
        inactive_delegators = [d for d in all_delegators if d.delegator_address not in active_delegators]

        for delegator in inactive_delegators:
            # Example for flagging as inactive
            delegator.active = False
            logger.debug(f"Flagging delegator {delegator.delegator_address} of validator {validator_address} as inactive.")
            # If deleting, uncomment the next line
            logger.info(f"Removing delegator {delegator.delegator_address} of validator {validator_address} from database.")
            session.delete(delegator)

        session.commit()
    except Exception as e:
        logger.error(f"An error occurred during cleanup: {e}")
        session.rollback()
    finally:
        session.close()

