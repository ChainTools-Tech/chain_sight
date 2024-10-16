import json
import logging

from dateutil import parser
from sqlalchemy.exc import IntegrityError

from chain_sight.models.models import Validator, ChainConfig, Delegator, GovernanceProposal
from chain_sight.services.database_config import Session

logger = logging.getLogger(__name__)


def insert_validator(validator_data, chain_id):
    session = Session()
    try:
        logger.debug(f"Received validator data: {validator_data}")
        chain_config = session.query(ChainConfig).filter_by(chain_id=chain_id).first()
        if not chain_config:
            logger.error(f"No chain configuration found for chain_id {chain_id}")
            return

        existing_validator = session.query(Validator).filter_by(
            operator_address=validator_data.get("operator_address")).first()

        if existing_validator:
            logger.info(f"Validator {validator_data.get('operator_address')} already exists. Skipping insertion.")
            return

        prepared_data = {
            "operator_address": validator_data.get("operator_address", ""),
            "consensus_pubkey": json.dumps(validator_data.get("consensus_pubkey", {})),
            "jailed": validator_data.get("jailed", False),
            "status": validator_data.get("status", ""),
            "tokens": int(validator_data.get("tokens", 0)),
            "delegator_shares": float(validator_data.get("delegator_shares", 0.0)),
            "moniker": validator_data.get("description", {}).get("moniker", ""),
            "identity": validator_data.get("description", {}).get("identity", ""),
            "website": validator_data.get("description", {}).get("website", ""),
            "security_contact": validator_data.get("description", {}).get("security_contact", ""),
            "details": validator_data.get("description", {}).get("details", ""),
            "commission_rate": float(validator_data.get("commission", {}).get("commission_rates", {}).get("rate", 0.0)),
            "commission_max_rate": float(validator_data.get("commission", {}).get("commission_rates", {}).get("max_rate", 0.0)),
            "commission_max_change_rate": float(validator_data.get("commission", {}).get("commission_rates", {}).get("max_change_rate", 0.0)),
            "min_self_delegation": int(validator_data.get("min_self_delegation", 1)),
            "chain_config_id": chain_config.id
        }

        validator = Validator(**prepared_data)
        session.add(validator)
        session.commit()
        logger.debug(f"Validator {validator_data.get('operator_address')} inserted successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()


def insert_delegator(delegator_data, validator_address):
    session = Session()
    try:
        delegation = delegator_data['delegation']
        balance = delegator_data['balance']
        # Check for existing delegator for this validator
        existing_delegator = session.query(Delegator).filter_by(delegator_address=delegation["delegator_address"],
                                                                validator_address=validator_address).first()

        if existing_delegator:
            # If existing, update balance_amount if it has changed
            if existing_delegator.balance_amount != int(balance["amount"]):
                existing_delegator.balance_amount = int(balance["amount"])
                session.commit()
                logger.debug(f"Updated balance for delegator {delegation['delegator_address']} of validator {validator_address}.")
        else:
            # If not existing, insert new delegator
            new_delegator = Delegator(
                delegator_address=delegation["delegator_address"],
                validator_address=validator_address,
                shares=delegation["shares"],
                balance_amount=int(balance["amount"]),
                balance_denom=balance["denom"]
            )
            session.add(new_delegator)
            session.commit()
            logger.debug(f"Inserted new delegator {delegation['delegator_address']} for validator {validator_address}.")

    except Exception as e:
        logger.error(f"An error occurred while processing delegator: {e}")
        session.rollback()
    finally:
        session.close()


def insert_or_update_governance_proposal(proposal_data, chain_id):
    session = Session()
    try:
        logger.debug(f"Attempting to insert/update proposal for chain_id '{chain_id}' with data: {proposal_data}")

        # Retrieve the chain configuration
        chain_config = session.query(ChainConfig).filter_by(chain_id=chain_id).first()
        if not chain_config:
            logger.error(f"No chain configuration found for chain_id '{chain_id}'. Proposal ID: {proposal_data.get('proposal_id')}")
            return

        # Extract proposal_id safely
        proposal_id = proposal_data.get("proposal_id")
        if not proposal_id:
            logger.error(f"Proposal data missing 'proposal_id'. Data: {proposal_data}")
            return

        # Check for existing proposal to prevent duplicates
        existing_proposal = session.query(GovernanceProposal).filter_by(proposal_id=proposal_id, chain_id=chain_id).first()

        if existing_proposal:
            logger.info(f"Governance proposal '{proposal_id}' for chain '{chain_id}' already exists. Skipping insertion.")
            return

        # Safely extract 'content'
        content = proposal_data.get("content", {})
        if not content:
            logger.error(f"Proposal '{proposal_id}' missing 'content' field. Data: proposal_data")
            return

        # Safely extract 'title' and 'description' with defaults
        title = content.get("title")
        if not title:
            logger.warning(f"Proposal '{proposal_id}' missing 'title'. Setting to 'No Title Provided'.")
            title = "No Title Provided"

        description = content.get("description")
        if not description:
            logger.warning(f"Proposal '{proposal_id}' missing 'description'. Setting to 'No Description Provided'.")
            description = "No Description Provided"

        # Safely extract '@type'
        proposal_type = content.get("@type")
        if not proposal_type:
            logger.warning(f"Proposal '{proposal_id}' missing '@type'. Setting to 'Unknown Type'.")
            proposal_type = "Unknown Type"

        # Safely extract 'summary' and 'proposer'
        summary = proposal_data.get("summary")
        if not summary:
            logger.warning(f"Proposal '{proposal_id}' missing 'summary'. Setting to 'No Summary Provided'.")
            summary = "No Summary Provided"

        proposer = proposal_data.get("proposer", "Unknown Proposer")
        if not proposer:
            logger.warning(f"Proposal '{proposal_id}' has an empty 'proposer'. Setting to 'Unknown Proposer'.")
            proposer = "Unknown Proposer"

        # Parse datetime fields safely
        submit_time = parser.parse(proposal_data["submit_time"]) if proposal_data.get("submit_time") else None
        deposit_end_time = parser.parse(proposal_data["deposit_end_time"]) if proposal_data.get("deposit_end_time") else None
        voting_start_time = parser.parse(proposal_data["voting_start_time"]) if proposal_data.get("voting_start_time") else None
        voting_end_time = parser.parse(proposal_data["voting_end_time"]) if proposal_data.get("voting_end_time") else None

        # Safely extract 'final_tally_result' with defaults
        final_tally = proposal_data.get("final_tally_result", {})
        yes_votes = int(final_tally.get("yes", 0))
        abstain_votes = int(final_tally.get("abstain", 0))
        no_votes = int(final_tally.get("no", 0))
        no_with_veto_votes = int(final_tally.get("no_with_veto", 0))

        # Safely extract 'total_deposit'
        total_deposit = proposal_data.get("total_deposit", [])

        # Create a new GovernanceProposal instance
        proposal = GovernanceProposal(
            proposal_id=proposal_id,
            chain_config_id=chain_config.id,
            chain_id=chain_id,
            title=title,
            summary=summary,
            description=description,
            proposal_type=proposal_type,
            status=proposal_data.get("status"),
            yes_votes=yes_votes,
            abstain_votes=abstain_votes,
            no_votes=no_votes,
            no_with_veto_votes=no_with_veto_votes,
            submit_time=submit_time,
            deposit_end_time=deposit_end_time,
            voting_start_time=voting_start_time,
            voting_end_time=voting_end_time,
            total_deposit=total_deposit,
            metadata=proposal_data.get("metadata")
        )

        # Add and commit the new proposal
        session.add(proposal)
        session.commit()
        logger.debug(f"Governance proposal '{proposal_id}' for chain '{chain_id}' inserted successfully.")

    except IntegrityError as e:
        # Handle database integrity errors (e.g., unique constraint violations)
        logger.error(f"Database integrity error for Proposal ID '{proposal_id}': {e}")
        logger.error(f"Proposal Data: {proposal_data}")
        session.rollback()
    except ValueError as e:
        # Handle value errors (e.g., type casting issues)
        logger.error(f"Value error processing Proposal ID '{proposal_id}': {e}")
        logger.error(f"Proposal Data: {proposal_data}")
        session.rollback()
    except Exception as e:
        # Handle any other unexpected exceptions
        logger.error(f"Unexpected error processing Proposal ID '{proposal_id}': {e}")
        logger.error(f"Proposal Data: {proposal_data}")
        session.rollback()
    finally:
        session.close()
