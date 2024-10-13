import pytest
from src import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def session():
    # Setup code
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session  # This is where the testing happens
    # Teardown code
    Base.metadata.drop_all(engine)

def test_insert_validator(session):
    # Use the session fixture to insert a validator and assert conditions
    pass
