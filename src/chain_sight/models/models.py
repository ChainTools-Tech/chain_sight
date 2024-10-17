from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Boolean, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from chain_sight.services.database_config import Base


class ChainConfig(Base):
    __tablename__ = 'chain_config'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # e.g., Mainnet, Testnet, etc.
    chain_id = Column(String, unique=True, nullable=False)  # Unique per chain (mainnet/testnet can differ)
    prefix = Column(String, nullable=False)
    rpc_endpoint = Column(String, nullable=False)
    api_endpoint = Column(String, nullable=False)
    grpc_endpoint = Column(String)

    # Relationships
    validators = relationship("Validator", back_populates="chain_config", cascade="all, delete")
    governance_proposals = relationship("GovernanceProposal", back_populates="chain_config", cascade="all, delete")
    delegators = relationship("Delegator", back_populates="chain_config", cascade="all, delete")

    def __repr__(self):
        return (f"<ChainConfig(id={self.id}, name='{self.name}', chain_id='{self.chain_id}', "
                f"prefix='{self.prefix}', rpc_endpoint='{self.rpc_endpoint}', "
                f"api_endpoint='{self.api_endpoint}', grpc_endpoint='{self.grpc_endpoint}')>")


class Validator(Base):
    __tablename__ = 'validators'
    id = Column(Integer, primary_key=True)
    operator_address = Column(String, index=True)  # Remove 'unique=True' and make it index instead
    consensus_pubkey = Column(String)
    jailed = Column(Boolean)
    status = Column(String)
    tokens = Column(Numeric(precision=60, scale=18))
    delegator_shares = Column(Numeric(precision=70, scale=30))
    moniker = Column(String)
    identity = Column(String)
    website = Column(String)
    security_contact = Column(String)
    details = Column(String)
    commission_rate = Column(Numeric(precision=20, scale=18))
    commission_max_rate = Column(Numeric(precision=20, scale=18))
    commission_max_change_rate = Column(Numeric(precision=20, scale=18))
    min_self_delegation = Column(Numeric(precision=50, scale=0))
    chain_config_id = Column(Integer, ForeignKey('chain_config.id'), nullable=False)

    # Composite unique constraint on operator_address and chain_config_id
    __table_args__ = (
        UniqueConstraint('operator_address', 'chain_config_id', name='uq_validator_operator_chain'),
    )

    # Relationships
    chain_config = relationship("ChainConfig", back_populates="validators")
    delegators = relationship("Delegator", back_populates="validator")

    def __repr__(self):
        return (f"<Validator(id={self.id}, operator_address='{self.operator_address}', "
                f"status='{self.status}', moniker='{self.moniker}', chain='{self.chain_config.name}')>")


class Delegator(Base):
    __tablename__ = 'delegators'
    id = Column(Integer, primary_key=True)
    delegator_address = Column(String, index=True)
    validator_address = Column(String, ForeignKey('validators.operator_address'))  # Links to validator
    shares = Column(Numeric(precision=60, scale=30))
    balance_amount = Column(Numeric(precision=60, scale=30))
    balance_denom = Column(String)
    chain_config_id = Column(Integer, ForeignKey('chain_config.id'), nullable=False)  # Link delegator to chain

    # Relationships
    validator = relationship("Validator", back_populates="delegators")
    chain_config = relationship("ChainConfig", back_populates="delegators")

    def __repr__(self):
        return (f"<Delegator(id={self.id}, delegator_address='{self.delegator_address}', "
                f"validator_address='{self.validator_address}', chain='{self.chain_config.name}')>")


class GovernanceProposal(Base):
    __tablename__ = 'governance_proposals'
    id = Column(Integer, primary_key=True)
    proposal_id = Column(String, nullable=False)  # From API, can be same across chains
    chain_id = Column(String, ForeignKey('chain_config.chain_id'), nullable=False)  # Maps to specific chain
    title = Column(String)
    description = Column(String)
    proposal_type = Column(String)
    status = Column(String)
    yes_votes = Column(Numeric(precision=80, scale=0))
    abstain_votes = Column(Numeric(precision=80, scale=0))
    no_votes = Column(Numeric(precision=80, scale=0))
    no_with_veto_votes = Column(Numeric(precision=80, scale=0))
    submit_time = Column(DateTime)
    deposit_end_time = Column(DateTime)
    total_deposit = Column(JSON)
    voting_start_time = Column(DateTime)
    voting_end_time = Column(DateTime)
    proposal_metadata = Column(String)
    proposer = Column(String)

    # Relationships
    chain_config = relationship("ChainConfig", back_populates="governance_proposals")

    def __repr__(self):
        return (f"<GovernanceProposal(id={self.id}, proposal_id='{self.proposal_id}', "
                f"title='{self.title}', chain='{self.chain_config.name}', status='{self.status}')>")
