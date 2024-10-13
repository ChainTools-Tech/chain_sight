from sqlalchemy import Column, Integer, String, Float, BigInteger, ForeignKey, DateTime, JSON, \
    Boolean
from sqlalchemy.orm import relationship
from services.database_config import Base


class ChainConfig(Base):
    __tablename__ = 'chain_config'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    chain_id = Column(String, unique=True, nullable=False)
    prefix = Column(String, nullable=False)
    rpc_endpoint = Column(String, nullable=False)
    api_endpoint = Column(String, nullable=False)
    grpc_endpoint = Column(String)

    # Relationships
    validators = relationship("Validator", back_populates="chain_config")
    governance_proposals = relationship("GovernanceProposal", back_populates="chain_config")


class Validator(Base):
    __tablename__ = 'validators'
    id = Column(Integer, primary_key=True)
    operator_address = Column(String, unique=True, index=True)
    consensus_pubkey = Column(String)
    jailed = Column(Boolean)
    status = Column(String)
    tokens = Column(BigInteger)
    delegator_shares = Column(Float)
    moniker = Column(String)
    identity = Column(String)
    website = Column(String)
    security_contact = Column(String)
    details = Column(String)
    commission_rate = Column(Float)
    commission_max_rate = Column(Float)
    commission_max_change_rate = Column(Float)
    min_self_delegation = Column(BigInteger)
    chain_config_id = Column(Integer, ForeignKey('chain_config.id'))

    # Relationships
    chain_config = relationship("ChainConfig", back_populates="validators")
    delegators = relationship("Delegator", back_populates="validator")


class Delegator(Base):
    __tablename__ = 'delegators'
    id = Column(Integer, primary_key=True)
    delegator_address = Column(String, index=True)
    validator_address = Column(String, ForeignKey('validators.operator_address'))
    shares = Column(String)
    balance_amount = Column(BigInteger)
    balance_denom = Column(String)

    # Relationship
    validator = relationship("Validator", back_populates="delegators")


class GovernanceProposal(Base):
    __tablename__ = 'governance_proposals'
    id = Column(Integer, primary_key=True)
    proposal_id = Column(String, nullable=False)
    chain_id = Column(String, nullable=False)
    title = Column(String)
    description = Column(String)
    proposal_type = Column(String)
    status = Column(String)
    yes_votes = Column(BigInteger)
    abstain_votes = Column(BigInteger)
    no_votes = Column(BigInteger)
    no_with_veto_votes = Column(BigInteger)
    submit_time = Column(DateTime)
    deposit_end_time = Column(DateTime)
    total_deposit = Column(JSON)
    voting_start_time = Column(DateTime)
    voting_end_time = Column(DateTime)
    chain_config_id = Column(Integer, ForeignKey('chain_config.id'))

    # Relationship
    chain_config = relationship("ChainConfig", back_populates="governance_proposals")
