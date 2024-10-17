import json
import logging

from dateutil import parser
from decimal import Decimal
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from chain_sight.models.models import Validator, ChainConfig, Delegator, GovernanceProposal
from chain_sight.services.database_config import Session

logger = logging.getLogger(__name__)


def insert_validator(validator_data, chain_id):
    """
    Inserts a new validator into the database.

    If the validator with the given `operator_address` already exists for the specified `chain_id`,
    the insertion is skipped.

    Args:
        validator_data (dict): The raw validator data fetched from the API.
        chain_id (str): The chain ID of the blockchain to which the validator belongs.

    Returns:
        None
    """
    session = Session()
    try:
        logger.debug(f"Received validator data: {validator_data}")

        # Fetch chain configuration by chain_id
        chain_config = session.query(ChainConfig).filter_by(chain_id=chain_id).first()
        if not chain_config:
            logger.error(f"No chain configuration found for chain_id {chain_id}")
            return

        # Check if validator already exists for this chain
        existing_validator = session.query(Validator).filter_by(
            operator_address=validator_data.get("operator_address"),
            chain_config_id=chain_config.id  # Ensure the validator is linked to this chain
        ).first()

        if existing_validator:
            logger.info(
                f"Validator {validator_data.get('operator_address')} already exists for chain {chain_id}. Skipping insertion.")
            return

        # Prepare the validator data for insertion
        prepared_data = {
            "operator_address": validator_data.get("operator_address", ""),
            "chain_config_id": chain_config.id,
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
            "commission_max_rate": float(
                validator_data.get("commission", {}).get("commission_rates", {}).get("max_rate", 0.0)),
            "commission_max_change_rate": float(
                validator_data.get("commission", {}).get("commission_rates", {}).get("max_change_rate", 0.0)),
            "min_self_delegation": int(validator_data.get("min_self_delegation", 1))
        }

        # Insert new validator into the database
        validator = Validator(**prepared_data)
        session.add(validator)
        session.commit()
        logger.debug(f"Validator {validator_data.get('operator_address')} for chain {chain_id} inserted successfully.")

    except IntegrityError as e:
        logger.error(f"IntegrityError occurred while inserting validator: {e}")
        session.rollback()
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemyError occurred: {e}")
        session.rollback()
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        session.rollback()
    finally:
        session.close()



def insert_delegator(delegator_data, validator_address, chain_id):
    """
    Inserts or updates a delegator associated with a specific validator and chain.

    If the delegator already exists for the given `validator_address` and `chain_id`,
    their balance is updated. Otherwise, a new delegator is inserted.

    Args:
        delegator_data (dict): The raw delegator data fetched from the API.
        validator_address (str): The address of the validator to whom the delegator is linked.
        chain_id (str): The chain ID of the blockchain to which the delegator belongs.

    Returns:
        None
    """
    session = Session()
    try:
        # Fetch chain configuration by chain_id
        chain_config = session.query(ChainConfig).filter_by(chain_id=chain_id).first()
        if not chain_config:
            logger.error(f"No chain configuration found for chain_id {chain_id}")
            return

        delegation = delegator_data['delegation']
        balance = delegator_data['balance']

        # Check for existing delegator linked to this validator and chain
        existing_delegator = session.query(Delegator).filter_by(
            delegator_address=delegation["delegator_address"],
            validator_address=validator_address,
            validator_chain_config_id=chain_config.id
        ).first()

        if existing_delegator:
            # Update balance if it has changed
            balance_amount = Decimal(balance["amount"])
            if existing_delegator.balance_amount != balance_amount:
                existing_delegator.balance_amount = balance_amount
                session.commit()
                logger.info(
                    f"Updated balance for delegator {delegation['delegator_address']} of validator {validator_address} on chain {chain_id}.")
        else:
            # Insert new delegator
            new_delegator = Delegator(
                delegator_address=delegation["delegator_address"],
                validator_address=validator_address,
                validator_chain_config_id=chain_config.id,
                shares=delegation["shares"],
                balance_amount=int(balance["amount"]),
                balance_denom=balance["denom"],
            )
            session.add(new_delegator)
            session.commit()
            logger.debug(
                f"Inserted new delegator {delegation['delegator_address']} for validator {validator_address} on chain {chain_id}.")

    except IntegrityError as e:
        logger.error(f"IntegrityError occurred while inserting delegator: {e}")
        session.rollback()
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemyError occurred: {e}")
        session.rollback()
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        session.rollback()
    finally:
        session.close()


def insert_or_update_governance_proposal(proposal_data, chain_id):
    """
    Inserts a new governance proposal or updates an existing one.

    If a proposal with the same `proposal_id` already exists for the specified `chain_id`,
    the proposal is updated with the latest data. Otherwise, it is inserted as a new proposal.

    Args:
        proposal_data (dict): The normalized proposal data.
        chain_id (str): The chain ID of the blockchain.

    Returns:
        None
    """
    session = Session()
    try:
        proposal_id = proposal_data['proposal_id']
        logger.debug(f"Processing Proposal ID {proposal_id} for Chain ID {chain_id}.")

        # Fetch chain configuration by chain_id
        chain_config = session.query(ChainConfig).filter_by(chain_id=chain_id).first()
        if not chain_config:
            logger.error(f"No chain configuration found for chain_id {chain_id}")
            return

        # Check if the proposal already exists for this chain
        existing_proposal = session.query(GovernanceProposal).filter_by(
            proposal_id=proposal_id, chain_config_id=chain_config.id
        ).first()

        if not existing_proposal:
            # Insert new proposal
            new_proposal = GovernanceProposal(
                proposal_id=proposal_id,
                chain_id=chain_id,
                chain_config_id=chain_config.id,  # Link the proposal to the chain configuration
                title=proposal_data.get('title'),
                description=proposal_data.get('summary'),
                proposal_type=proposal_data.get('content', {}).get('@type'),
                status=proposal_data.get('status'),
                yes_votes=int(proposal_data['final_tally_result']['yes']),
                abstain_votes=int(proposal_data['final_tally_result']['abstain']),
                no_votes=int(proposal_data['final_tally_result']['no']),
                no_with_veto_votes=int(proposal_data['final_tally_result']['no_with_veto']),
                submit_time=parser.parse(proposal_data['submit_time']),
                deposit_end_time=parser.parse(proposal_data['deposit_end_time']),
                voting_start_time=parser.parse(proposal_data['voting_start_time']),
                voting_end_time=parser.parse(proposal_data['voting_end_time']),
                total_deposit=proposal_data['total_deposit'],
                proposal_metadata=proposal_data.get('metadata'),
                proposer=proposal_data.get('proposer')
            )
            session.add(new_proposal)
            logger.info(f"Inserted new governance proposal: {proposal_id} on chain {chain_id}")
        else:
            # Update existing proposal
            existing_proposal.status = proposal_data.get('status')
            existing_proposal.yes_votes = int(proposal_data['final_tally_result']['yes'])
            existing_proposal.abstain_votes = int(proposal_data['final_tally_result']['abstain'])
            existing_proposal.no_votes = int(proposal_data['final_tally_result']['no'])
            existing_proposal.no_with_veto_votes = int(proposal_data['final_tally_result']['no_with_veto'])
            existing_proposal.title = proposal_data.get('title')
            existing_proposal.description = proposal_data.get('summary')
            existing_proposal.proposal_metadata = proposal_data.get('metadata')
            session.commit()
            logger.info(f"Updated governance proposal: {proposal_id} on chain {chain_id}")

        session.commit()

    except IntegrityError as e:
        logger.error(f"IntegrityError: {e}")
        session.rollback()
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemyError: {e}")
        session.rollback()
    except KeyError as e:
        logger.error(f"KeyError: Missing {e} in proposal data for Proposal ID {proposal_data.get('proposal_id')}")
        session.rollback()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        session.rollback()
    finally:
        session.close()