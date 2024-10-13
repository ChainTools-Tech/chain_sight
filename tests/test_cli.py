import pytest
from click.testing import CliRunner
from src import fetch_and_store_validators, fetch_and_store_governance_proposals


@pytest.fixture
def runner():
    """Fixture for invoking command-line interfaces."""
    return CliRunner()

def test_fetch_and_store_validators_command(runner):
    """Test the fetch_and_store_validators CLI command."""
    with runner.isolated_filesystem():
        result = runner.invoke(fetch_and_store_validators, ['BitSong'])
        assert result.exit_code == 0
        assert 'Validators and their delegators for test_chain fetched and stored successfully.' in result.output

def test_fetch_and_store_governance_proposals_command(runner):
    """Test the fetch_and_store_governance_proposals CLI command."""
    with runner.isolated_filesystem():
        result = runner.invoke(fetch_and_store_governance_proposals, ['BitSong'])
        assert result.exit_code == 0
        assert 'Governance proposals for test_chain fetched and stored successfully.' in result.output
