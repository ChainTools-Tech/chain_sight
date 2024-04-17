# ChainSight

ChainSight is a blockchain data aggregator tool designed to collect and store information from various blockchain networks. It provides functionalities to fetch validators, delegators, and governance proposals data, making it easier for users to analyze blockchain activities and metrics.

## Features

- Fetch and store basic information about blockchain networks including validators, delegators, and governance proposals.
- Command-line interface for easy interaction with the tool.
- Configurable to support multiple blockchain networks through a simple JSON configuration.
- Logging support for monitoring operations and debugging.
- Utilizes SQLAlchemy for database operations, allowing for flexibility in database choice (SQLite by default, with support for PostgreSQL).

## Installation

To get started with ChainSight, you will need to have Python installed on your system. ChainSight has been tested with Python 3.8+.

1. Clone the repository:

```bash
git clone https://github.com/ChainTools-Tech/ChainSight.git
cd ChainSight
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

ChainSight provides a CLI for interacting with blockchain data. Below are some examples of how to use it:

- Fetch and store validators and their delegators for a specified chain:

```bash
python main.py fetch-and-store-validators <CHAIN_NAME>
```

- Fetch and store governance proposals for a specified chain:

```bash
python main.py fetch-and-store-governance-proposals <CHAIN_NAME>
```

Replace `<CHAIN_NAME>` with the name of the blockchain network as configured in your `chains.json` configuration file.

## Configuration

Blockchain networks and their RPC/API endpoints are configured in `config/chains.json`. Add or modify entries in this file to include the blockchains you're interested in:

```json
{
  "chains": [
    {
      "name": "chain_name",
      "chain_id": "chain_id",
      "rpc_endpoint": "http://rpc.node.url",
      "api_endpoint": "http://api.node.url",
      "grpc_endpoint": "http://grpc.node.url"
    }
  ]
}
```

## Testing

To run tests, use the following command:

```bash
pytest tests/
```

Ensure you have `pytest` installed, or install it via `pip install pytest`.

## Contributing

Contributions to ChainSight are welcome! Please refer to CONTRIBUTING.md for guidelines on how to contribute to this project.

## License

ChainSight is released under the MIT License. See the LICENSE file for more details.

