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
                insert_delegator(entry, validator_addr, chain_config.chain_id)
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
    Fetches governance proposals from the blockchain network.
    Tries '/v1/proposals' first, then falls back to '/v1beta1/proposals'.

    Args:
        chain_config (ChainConfig): Chain configuration object.

    Returns:
        list: A list of normalized governance proposals.
    """
    # Define both endpoints and try the preferred one first
    endpoints = [
        f"{chain_config.api_endpoint}/cosmos/gov/v1/proposals",
        f"{chain_config.api_endpoint}/cosmos/gov/v1beta1/proposals"
    ]

    proposals = []
    selected_endpoint = None
    version = None

    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, params={'pagination.limit': 1}, timeout=10)
            if response.status_code == 200:
                selected_endpoint = endpoint
                version = 'v1' if 'v1/proposals' in endpoint else 'v1beta1'
                logger.info(f"Using endpoint: {selected_endpoint} (API version: {version})")
                break
        except requests.RequestException as e:
            logger.warning(f"Failed to connect to {endpoint}: {e}")

    if not selected_endpoint:
        logger.error("No proposals endpoint available.")
        return proposals

    return _fetch_all_proposals(selected_endpoint, version)


def _fetch_all_proposals(endpoint, version):
    """
    Fetches and normalizes all governance proposals with pagination.
    """
    all_proposals = []
    next_key = None
    page_number = 0

    while True:
        params = {'pagination.limit': 100}
        if next_key:
            params['pagination.key'] = next_key

        try:
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:
                data = response.json()
                proposals = data.get('proposals', [])
                for proposal in proposals:
                    normalized = _normalize_proposal(proposal, version)
                    if normalized:
                        all_proposals.append(normalized)

                next_key = data.get('pagination', {}).get('next_key')
                if not next_key:
                    break
                page_number += 1
            else:
                logger.error(f"Failed to fetch proposals. Status code: {response.status_code}")
                break
        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            break

    return all_proposals


def _normalize_proposal(proposal, version):
    """
    Normalize a governance proposal based on the API version.

    Args:
        proposal (dict): Raw proposal data from API.
        version (str): API version ('v1' or 'v1beta1').

    Returns:
        dict: A normalized governance proposal.
    """
    if version == 'v1':
        # Safely access 'messages' and ensure it has at least one element
        messages = proposal.get("messages", [])
        content = messages[0] if messages else {}

        return {
            "proposal_id": proposal.get("id"),
            "content": content,
            "status": proposal.get("status"),
            "final_tally_result": {
                "yes": proposal.get("final_tally_result", {}).get("yes_count"),
                "abstain": proposal.get("final_tally_result", {}).get("abstain_count"),
                "no": proposal.get("final_tally_result", {}).get("no_count"),
                "no_with_veto": proposal.get("final_tally_result", {}).get("no_with_veto_count")
            },
            "submit_time": proposal.get("submit_time"),
            "deposit_end_time": proposal.get("deposit_end_time"),
            "total_deposit": proposal.get("total_deposit", []),  # Add total_deposit
            "voting_start_time": proposal.get("voting_start_time"),
            "voting_end_time": proposal.get("voting_end_time"),
            "metadata": proposal.get("metadata"),
            "title": proposal.get("title"),
            "summary": proposal.get("summary"),
            "proposer": proposal.get("proposer")
        }
    else:  # v1beta1
        content = proposal.get("content", {})
        return {
            "proposal_id": proposal.get("proposal_id"),
            "content": content,
            "status": proposal.get("status"),
            "final_tally_result": {
                "yes": proposal.get("final_tally_result", {}).get("yes"),
                "abstain": proposal.get("final_tally_result", {}).get("abstain"),
                "no": proposal.get("final_tally_result", {}).get("no"),
                "no_with_veto": proposal.get("final_tally_result", {}).get("no_with_veto")
            },
            "submit_time": proposal.get("submit_time"),
            "deposit_end_time": proposal.get("deposit_end_time"),
            "total_deposit": proposal.get("total_deposit", []),  # Add total_deposit
            "voting_start_time": proposal.get("voting_start_time"),
            "voting_end_time": proposal.get("voting_end_time"),
            "metadata": content.get("metadata"),
            "title": content.get("title"),
            "summary": content.get("description"),
            "proposer": proposal.get("proposer", "")
        }


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

