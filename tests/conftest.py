import os
import yaml
import pytest
from terraform_analyzer.models.repository import RepositoryInfo, AnalysisResult

def load_test_config():
    """Load test configuration from YAML file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'test_config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

@pytest.fixture
def test_config():
    """Fixture providing test configuration."""
    return load_test_config()

@pytest.fixture
def repo_info(test_config):
    """Fixture for creating a test RepositoryInfo from config."""
    repo = test_config['test_repositories'][0]  # Use first repository by default
    return RepositoryInfo(
        name=repo['name'],
        repository=repo['repository'],
        terraform_path=repo['terraform-path'],
        branch=repo['branch']
    )

@pytest.fixture
def repo_info_2(test_config):
    """Fixture for creating a second test RepositoryInfo from config."""
    repo = test_config['test_repositories'][1]  # Use second repository
    return RepositoryInfo(
        name=repo['name'],
        repository=repo['repository'],
        terraform_path=repo['terraform-path'],
        branch=repo['branch']
    )

@pytest.fixture
def analysis_result(repo_info):
    """Fixture for creating a test AnalysisResult."""
    return AnalysisResult(
        repository=repo_info,
        terraform_version="1.0.0",
        provider_versions={"aws": "4.0.0"},
        error=None
    )