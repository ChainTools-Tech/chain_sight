from diagrams import Diagram, Cluster
from diagrams.generic.blank import Blank
from diagrams.generic.os import CLI

with Diagram("ChainSight CLI Workflow", show=False):
    cli = CLI("CLI")

    with Cluster("Commands"):
        fetchValidators = Blank("fetch_and_store_validators")
        fetchProposals = Blank("fetch_and_store_governance_proposals")

    cli >> fetchValidators
    cli >> fetchProposals
