# Chain Sight

Chain Sight is a command-line tool designed for fetching blockchain data (validators and governance proposals) and storing it in a PostgreSQL database. It supports multiple blockchain networks and allows users to manage chain configurations and fetch data efficiently via the command line.
Features

- Fetch Validators: Retrieve validator data from various blockchain networks.
- Fetch Governance Proposals: Retrieve governance proposal data.
- Manage Chain Configurations: Easily import and display chain configurations from a JSON file.

## Installation

Clone the repository:

```bash
git clone https://github.com/ChainTools-Tech/chain_sight.git
cd chain_sight
```

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

Create a .env file to store the PostgreSQL database URL (example below):

```aiignore
DATABASE_URL=postgresql://user:password@localhost/chain_sight_db
```

Set up the PostgreSQL database using your preferred method.

## Configuration File

The configuration file (chains.json) contains details about the chains for which you want to fetch data. Below is an example configuration:

```json
{
  "chains": [
    {
      "name": "AssetMantle",
      "chain_id": "mantle-1",
      "prefix": "mantle",
      "rpc_endpoint": "https://rpc.assetmantle.one",
      "api_endpoint": "https://rest.assetmantle.one",
      "grpc_endpoint": "https://grpc.assetmantle.nodestake.top:443"
    },
    {
      "name": "Beezee",
      "chain_id": "beezee-1",
      "prefix": "bze",
      "rpc_endpoint": "https://rpc.beezee.chaintools.tech",
      "api_endpoint": "https://api.beezee.chaintools.tech",
      "grpc_endpoint": "https://grpc.beezee.chaintools.tech"
    }
  ]
}
```

Chain Configuration Fields:

- `name`: The name of the chain (e.g., AssetMantle, Beezee).
- `chain_id`: The unique identifier of the chain.
- `prefix`: The prefix for addresses on the chain.
- `rpc_endpoint`: The RPC endpoint for accessing the chain’s node.
- `api_endpoint`: The REST API endpoint for accessing blockchain data.
- `grpc_endpoint`: The gRPC endpoint for querying blockchain information.

## CLI Usage

The Chain Sight CLI provides a way to import or display chain configurations and fetch data from the blockchain.
General Usage

```bash
chain_sight --config [import|display] [--config-path CONFIG_PATH] [--log-file LOG_FILE] [--log-level LOG_LEVEL]
chain_sight --fetch [validators|governance] --chain CHAIN_ID [--log-file LOG_FILE] [--log-level LOG_LEVEL]
```

### Options and Parameters
`--config`

Manage the chain configurations.

```bash
import: Import chain configurations from a JSON file.
    Requires --config-path to specify the JSON file.
display: Display the existing chain configurations stored in the database.
```

Example:

```bash
chain_sight --config import --config-path /path/to/chains.json
```
This imports the chain configurations from the chains.json file.

```bash
chain_sight --config display
```
This displays the chain configurations stored in the database.

`--fetch`

Fetch blockchain data (validators or governance proposals).

```
validators: Fetch validator data for the specified chain.
governance: Fetch governance proposal data for the specified chain.
--chain: Specify the chain for which data should be fetched. The chain ID must match one of the configurations in the database.
```

Example:

```bash
chain_sight --fetch validators --chain mantle-1
```
This fetches validator data for the mantle-1 chain.

```bash
chain_sight --fetch governance --chain mantle-1
```
This fetches governance proposal data for the mantle-1 chain.

`--config-path`

Specify the path to the configuration file for import when using --config import.
Example:

```bash
chain_sight --config import --config-path /path/to/chains.json
```

`--log-file`

Specify a custom log file path (optional). Defaults to chain_sight.log.
Example:

```bash
chain_sight --fetch validators --chain mantle-1 --log-file /logs/validators.log
```

`--log-level`
Set the log level for logging output. Defaults to INFO. Options are:

    DEBUG
    INFO
    WARNING
    ERROR
    CRITICAL

Example:

```bash
chain_sight --fetch governance --chain mantle-1 --log-level DEBUG
```

## Workflow
1. Import Chain Configurations

Use the `--config import` option with the `--config-path` argument to import chain configurations from a JSON file.

```bash
chain_sight --config import --config-path /path/to/chains.json
```

2. Display Chain Configurations

Display the chain configurations that are currently stored in the database.

```bash
chain_sight --config display
```

3. Fetch Validator Data

Once the configurations are imported, you can fetch validator data for a specific chain by using the --fetch validators option and specifying the chain ID.

```bash
chain_sight --fetch validators --chain mantle-1
```

4. Fetch Governance Proposals

You can also fetch governance proposals for a chain by using the --fetch governance option and specifying the chain ID.

```bash
chain_sight --fetch governance --chain mantle-1
```

## Logging

Logging is configured to output both to the console and a log file. By default, the log file is chain_sight.log, but you can specify a custom log file using the --log-file option.

The log level defaults to INFO, but you can adjust it using the --log-level option. Available levels include DEBUG, INFO, WARNING, ERROR, and CRITICAL.