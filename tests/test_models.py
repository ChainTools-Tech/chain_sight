import pytest
from src.models.models import Validator, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="module")
def engine():
    return create_engine('sqlite:///:memory:')

@pytest.fixture(scope="module")
def session(engine):
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_validator_insertion(session):
    validator = Validator(operator_address="val1", consensus_pubkey="pubkey1", jailed=False, status="active", tokens=1000)
    session.add(validator)
    session.commit()
    assert session.query(Validator).count() == 1
    assert session.query(Validator).first().operator_address == "val1"
