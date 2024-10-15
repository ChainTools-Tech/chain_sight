import json

def load_config(chain_name=None):
    """Load chain configuration. Optionally, filter by chain name."""
    with open('config/chains.json', 'r') as f:
        config = json.load(f)
    if chain_name:
        # Filter for the specified chain
        chain_config = next((item for item in config["chains"] if item["name"] == chain_name), None)
        return chain_config
    return config
