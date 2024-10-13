import pytest
from src import insert_validator
from src import Base, Validator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_insert_validator(db_session):
    # Mock or construct the validator_data as received from fetch_validators
    validator_data = {
        "operator_address": "val1",
        "consensus_pubkey": "pubkey1",
        "jailed": False,
        "status": "active",
        "tokens": 1000
        # Add all required fields
    }
    insert_validator(validator_data)  # You may need to adjust this if your function requires more parameters
    assert db_session.query(Validator).count() == 1
    validator = db_session.query(Validator).first()
    assert validator.operator_address == "val1"
