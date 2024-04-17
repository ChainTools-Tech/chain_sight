from diagrams import Diagram
from diagrams.generic.database import SQL
from diagrams.generic.blank import Blank

with Diagram("ChainSight Data Models", show=False):
    validator = SQL("Validator")
    delegator = SQL("Delegator")
    governanceProposal = SQL("GovernanceProposal")

    validator >> delegator  # Indicates Validator has a relationship with Delegator
    validator >> governanceProposal  # Example, if such a relationship exists
