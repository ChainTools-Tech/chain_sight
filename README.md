# ChainSight

**ChainSight** is a powerful CLI tool designed for managing blockchain configurations and fetching essential blockchain data. It streamlines the process of importing, displaying, and updating blockchain configurations, as well as fetching validators and governance proposals from various blockchain networks. ChainSight ensures your configurations are always up-to-date and synchronized with your database, eliminating the need for manual database manipulations.

![ChainSight Logo](https://example.com/logo.png) <!-- Replace with your actual logo URL -->

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Example Configuration File](#example-configuration-file)
- [Usage](#usage)
  - [Importing Configurations](#importing-configurations)
  - [Displaying Configurations](#displaying-configurations)
  - [Fetching Data](#fetching-data)
    - [Fetching Validators](#fetching-validators)
    - [Fetching Governance Proposals](#fetching-governance-proposals)
- [Logging](#logging)
- [Database Migrations](#database-migrations)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Dynamic Configuration Import:** Easily import blockchain configurations from a JSON file into your database, with automatic detection and updating of existing configurations.
- **Configuration Display:** Retrieve and display current blockchain configurations from the database in a structured JSON format.
- **Data Fetching:** Fetch and store validators and governance proposals from supported blockchain networks.
- **Robust Logging:** Comprehensive logging with options for both standard and JSON formats to facilitate monitoring and debugging.
- **Database Migration Support:** Seamlessly manage database schema changes using Alembic.
- **Flexible CLI:** User-friendly command-line interface with clear parameters and options.

## Prerequisites

Before installing ChainSight, ensure you have the following prerequisites met:

- **Python 3.8+** installed on your system.
- **PostgreSQL** (or your preferred database) set up and running.
- **Git** installed for cloning the repository.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/chain_sight.git
   cd chain_sight

    Create a Virtual Environment:

    It's recommended to use a virtual environment to manage dependencies.

    bash

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install Dependencies:

bash

pip install -r requirements.txt

Set Up the Database:

Ensure your database is running and accessible. Update the database connection string in chain_sight/services/database_config.py accordingly.

Run Database Migrations:

Initialize Alembic and apply migrations to set up the database schema.

bash

    alembic upgrade head

Configuration

ChainSight uses a JSON configuration file to manage blockchain configurations. This file defines the various blockchain networks your application will interact with.
Example Configuration File

Create a JSON file (e.g., chains.json) with the following structure:

json

{
    "chains": [
        {
            "name": "Cosmos Hub",
            "chain_id": "cosmoshub-4",
            "prefix": "cosmos",
            "rpc_endpoint": "https://rpc.cosmos.network",
            "api_endpoint": "https://api.cosmos.network",
            "grpc_endpoint": "https://grpc.cosmos.network"
        },
        {
            "name": "Kava",
            "chain_id": "kava-6",
            "prefix": "kava",
            "rpc_endpoint": "https://rpc.kava.io",
            "api_endpoint": "https://api.kava.io",
            "grpc_endpoint": "https://grpc.kava.io"
        },
        {
            "name": "Osmosis",
            "chain_id": "osmosis-1",
            "prefix": "osmo",
            "rpc_endpoint": "https://rpc.osmosis.zone",
            "api_endpoint": "https://api.osmosis.zone",
            "grpc_endpoint": "https://grpc.osmosis.zone"
        }
        // Add more chains as needed
    ]
}

Field Descriptions:

    name: The human-readable name of the blockchain network.
    chain_id: The unique identifier for the blockchain network.
    prefix: The address prefix used in the blockchain.
    rpc_endpoint: The RPC endpoint URL for interacting with the blockchain.
    api_endpoint: The API endpoint URL for fetching blockchain data.
    grpc_endpoint: The gRPC endpoint URL for advanced interactions (optional).

Usage

ChainSight offers a range of command-line options to manage configurations and fetch blockchain data. Below are detailed descriptions of all available parameters and example usage scenarios.
Command-Line Parameters
Parameter	Type	Description
--config	String	Selects configuration mode. Choices: import, display.
--config-path	String	Path to the configuration JSON file. Required when --config is import.
--fetch	String	Selects fetch mode. Choices: validators, governance.
--chain	String	Specifies the blockchain network (e.g., cosmoshub-4). Required when --fetch is used.
--log-file	String	Sets the path for the log file. Defaults to chain_sight.log.
--log-level	String	Sets the logging level. Choices: DEBUG, INFO, WARNING, ERROR, CRITICAL. Defaults to INFO.
Importing Configurations

Description: Imports blockchain configurations from a JSON file into the database. If a chain already exists, it updates the existing configuration based on differences detected in the import file.

Command:

bash

python cli.py --config import --config-path /path/to/chains.json --log-file import.log --log-level DEBUG

Parameters:

    --config import: Selects the import mode.
    --config-path /path/to/chains.json: Specifies the path to the configuration file.
    --log-file import.log: (Optional) Sets the log file path.
    --log-level DEBUG: (Optional) Sets the logging level to DEBUG for detailed logs.

Output:

    Adds new chains to the database.
    Updates existing chains if parameters differ from the import file.
    Logs a summary of chains added, updated, and skipped.

Displaying Configurations

Description: Retrieves and displays all current blockchain configurations from the database in JSON format, mirroring the structure of the original configuration file.

Command:

bash

python cli.py --config display --log-file display.log --log-level INFO

Parameters:

    --config display: Selects the display mode.
    --log-file display.log: (Optional) Sets the log file path.
    --log-level INFO: (Optional) Sets the logging level to INFO.

Output:

json

{
    "chains": [
        {
            "name": "Cosmos Hub",
            "chain_id": "cosmoshub-4",
            "prefix": "cosmos",
            "rpc_endpoint": "https://rpc.cosmos.network",
            "api_endpoint": "https://api.cosmos.network",
            "grpc_endpoint": "https://grpc.cosmos.network"
        },
        {
            "name": "Kava",
            "chain_id": "kava-6",
            "prefix": "kava",
            "rpc_endpoint": "https://rpc.kava.io",
            "api_endpoint": "https://api.kava.io",
            "grpc_endpoint": "https://grpc.kava.io"
        }
        // More chains...
    ]
}

Fetching Data

ChainSight can fetch and store data related to validators and governance proposals from specified blockchain networks.
Fetching Validators

Description: Fetches validator data for a specified blockchain network and stores it in the database.

Command:

bash

python cli.py --fetch validators --chain cosmoshub-4 --log-file fetch_validators.log --log-level WARNING

Parameters:

    --fetch validators: Selects the validators fetch mode.
    --chain cosmoshub-4: Specifies the blockchain network.
    --log-file fetch_validators.log: (Optional) Sets the log file path.
    --log-level WARNING: (Optional) Sets the logging level to WARNING.

Output:

    Fetches validator data from the specified blockchain.
    Stores or updates validator information in the database.
    Logs success or failure messages.

Fetching Governance Proposals

Description: Fetches governance proposals for a specified blockchain network and stores them in the database.

Command:

bash

python cli.py --fetch governance --chain cosmoshub-4 --log-file fetch_governance.log --log-level ERROR

Parameters:

    --fetch governance: Selects the governance proposals fetch mode.
    --chain cosmoshub-4: Specifies the blockchain network.
    --log-file fetch_governance.log: (Optional) Sets the log file path.
    --log-level ERROR: (Optional) Sets the logging level to ERROR.

Output:

    Fetches governance proposal data from the specified blockchain.
    Stores or updates governance proposals in the database.
    Logs success or failure messages.

Logging

ChainSight provides robust logging capabilities to facilitate monitoring and debugging.
Log Formats

    Standard (Plain-Text) Logging:
        Console Output:

        yaml

2024-04-27 10:15:30,123 [INFO] chain_sight.services.commands: Added new chain configuration: Cosmos Hub
2024-04-27 10:16:45,456 [ERROR] chain_sight.services.commands: An error occurred during configuration import: ConnectionTimeout

Log File (chain_sight.log):

yaml

    2024-04-27 10:15:30,123 [INFO] chain_sight.services.commands: Added new chain configuration: Cosmos Hub
    2024-04-27 10:16:45,456 [ERROR] chain_sight.services.commands: An error occurred during configuration import: ConnectionTimeout

JSON Logging (Structured Logging):

    Console Output:

    yaml

2024-04-27T10:15:30.123Z [INFO] chain_sight.services.commands: Added new chain configuration: Cosmos Hub
2024-04-27T10:16:45.456Z [ERROR] chain_sight.services.commands: An error occurred during configuration import: ConnectionTimeout

Log File (chain_sight.log):

json

        {
            "asctime": "2024-04-27T10:15:30.123Z",
            "levelname": "INFO",
            "name": "chain_sight.services.commands",
            "message": "Added new chain configuration: Cosmos Hub"
        }
        {
            "asctime": "2024-04-27T10:16:45.456Z",
            "levelname": "ERROR",
            "name": "chain_sight.services.commands",
            "message": "An error occurred during configuration import: ConnectionTimeout"
        }

Configuring Logging

You can configure the logging format by modifying the setup_logging function in cli.py. By default, ChainSight logs to both a file and the console with configurable log levels.
Example: JSON Logging Configuration

python

import logging
from pythonjsonlogger import jsonlogger
import sys

def setup_logging(log_file, log_level):
    """
    Configures logging to use both file and console handlers with JSON formatting.
    
    Args:
        log_file (str): Path to the log file.
        log_level (str): Logging level as a string (e.g., 'DEBUG', 'INFO').
    """
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Create handlers
    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler(sys.stdout)

    # Create JSON formatter
    json_formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')

    # Assign formatters to handlers
    file_handler.setFormatter(json_formatter)
    console_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

Note: Ensure you have the python-json-logger package installed:

bash

pip install python-json-logger

Database Migrations

ChainSight uses Alembic for managing database schema migrations, ensuring that your database stays in sync with your SQLAlchemy models.
Setting Up Alembic

    Install Alembic:

    bash

pip install alembic

Initialize Alembic:

bash

alembic init alembic

Configure Alembic:

    Update alembic.ini: Set your database connection string.

    ini

sqlalchemy.url = postgresql://user:password@localhost:5432/yourdatabase

Update alembic/env.py: Import your SQLAlchemy models to enable Alembic to detect changes.

python

    # alembic/env.py
    from logging.config import fileConfig
    from sqlalchemy import engine_from_config
    from sqlalchemy import pool
    from alembic import context

    import sys
    sys.path.append('.')
    from chain_sight.services.database_config import Base  # Adjust the path as necessary

    # this is the Alembic Config object, which provides
    # access to the values within the .ini file in use.
    config = context.config

    # Interpret the config file for Python logging.
    # This line sets up loggers basically.
    fileConfig(config.config_file_name)

    target_metadata = Base.metadata

Create a Migration Script:

Generate a new migration script to reflect changes in your models.

bash

alembic revision --autogenerate -m "Initial migration"

Apply Migrations:

bash

    alembic upgrade head

Important: Always back up your database before applying migrations, especially those that alter existing columns or data types.
Testing

To ensure the reliability and correctness of ChainSight, implement both unit and integration tests.
Running Tests

    Install Testing Dependencies:

    Add testing libraries to your requirements.txt or install them directly.

    bash

pip install pytest pytest-cov

Write Tests:

Create test modules in a tests/ directory. For example, tests/test_commands.py.

Run Tests:

bash

pytest --cov=chain_sight

Generate Coverage Report:

bash

    pytest --cov=chain_sight --cov-report=html

    Open htmlcov/index.html in your browser to view the coverage report.

Contributing

Contributions are welcome! If you have suggestions, bug reports, or want to contribute code, please follow the guidelines below.
Steps to Contribute

    Fork the Repository:

    Click the "Fork" button at the top-right corner of the repository page.

    Clone Your Fork:

    bash

git clone https://github.com/yourusername/chain_sight.git
cd chain_sight

Create a New Branch:

bash

git checkout -b feature/your-feature-name

Make Your Changes:

Implement your feature or bug fix.

Commit Your Changes:

bash

git commit -m "Add feature: your feature description"

Push to Your Fork:

bash

    git push origin feature/your-feature-name

    Create a Pull Request:

    Navigate to the original repository and click "New pull request". Provide a clear description of your changes.

Code of Conduct

Please adhere to the Code of Conduct when contributing to this project.
License

This project is licensed under the MIT License.
Contact

For any questions, suggestions, or support, please reach out:

    Email: your.email@example.com
    GitHub Issues: Issues Page
    LinkedIn: Your LinkedIn Profile

<!-- Replace with your actual image URL -->

markdown


---

# Additional Notes:

1. **Replace Placeholder URLs:** Ensure you replace placeholder URLs (e.g., logo URLs, repository URLs, contact information) with your actual project's details.

2. **Dependencies:** The `requirements.txt` should include all necessary dependencies, such as `SQLAlchemy`, `python-json-logger`, `alembic`, etc.

3. **Database Configuration:** The `chain_sight/services/database_config.py` should contain your SQLAlchemy engine and session setup.

4. **Testing:** Provide actual tests in the `tests/` directory for unit and integration testing.

5. **License and Code of Conduct:** Include `LICENSE` and `CODE_OF_CONDUCT.md` files in your repository as referenced.

6. **Consistency:** Ensure that the descriptions, commands, and examples accurately reflect your application's functionality and current state.

