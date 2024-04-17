from diagrams import Diagram, Cluster
from diagrams.generic.blank import Blank

with Diagram("ChainSight Module Relationships", show=False):
    with Cluster("src"):
        with Cluster("common"):
            utils = Blank("utils.py")

        with Cluster("models"):
            models = Blank("models.py")

        with Cluster("services"):
            blockchain = Blank("blockchain.py")
            database = Blank("database.py")

        with Cluster("cli"):
            commands = Blank("commands.py")

    models >> database  # Indicates models.py is used by database.py
    blockchain >> database  # blockchain.py interacts with database.py
    commands >> [blockchain, database]  # commands.py uses both services
