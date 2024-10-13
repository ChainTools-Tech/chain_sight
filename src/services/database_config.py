import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


logger = logging.getLogger(__name__)

load_dotenv()

Base = declarative_base()

# Environment-based configuration for database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///chainsight.db')

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def initialize_database():
    Base.metadata.create_all(engine)