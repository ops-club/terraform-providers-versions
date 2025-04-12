import pytest
from terraform_analyzer.models.repository import RepositoryInfo, AnalysisResult

@pytest.fixture
def repo_info(test_config):
    """Load repository info from test config."""
    repo = test_config['test_repositories'][0]
    return RepositoryInfo(
        name=repo['name'],
        repository=repo['repository'],
        terraform_path=repo['terraform-path'],
        branch=repo['branch']
    )

def test_repository_info_creation(test_config):
    """Test la création d'un RepositoryInfo avec tous les paramètres."""
    repo_config = test_config['test_repositories'][0]
    repo = RepositoryInfo(
        name=repo_config['name'],
        repository=repo_config['repository'],
        terraform_path=repo_config['terraform-path'],
        branch=repo_config['branch']
    )
    
    assert repo.name == repo_config['name']
    assert repo.repository == repo_config['repository']
    assert repo.terraform_path == repo_config['terraform-path']
    assert repo.branch == repo_config['branch']

def test_repository_info_creation_without_branch(test_config):
    """Test la création d'un RepositoryInfo sans branche spécifiée."""
    repo_config = test_config['test_repositories'][0]
    repo = RepositoryInfo(
        name=repo_config['name'],
        repository=repo_config['repository'],
        terraform_path=repo_config['terraform-path']
    )
    
    assert repo.name == repo_config['name']
    assert repo.repository == repo_config['repository']
    assert repo.terraform_path == repo_config['terraform-path']
    assert repo.branch is None

def test_analysis_result_creation(repo_info):
    """Test la création d'un AnalysisResult avec tous les paramètres."""
    result = AnalysisResult(
        repository=repo_info,
        terraform_version="1.0.0",
        provider_versions={"aws": "4.0.0"},
        error=None
    )
    
    assert result.repository == repo_info
    assert result.terraform_version == "1.0.0"
    assert result.provider_versions == {"aws": "4.0.0"}
    assert result.error is None

def test_analysis_result_creation_with_error(repo_info):
    """Test la création d'un AnalysisResult avec une erreur."""
    result = AnalysisResult(
        repository=repo_info,
        error="Test error"
    )
    
    assert result.repository == repo_info
    assert result.terraform_version is None
    assert result.provider_versions == {}
    assert result.error == "Test error"

def test_analysis_result_default_provider_versions(repo_info):
    """Test que provider_versions est initialisé comme un dictionnaire vide par défaut."""
    result = AnalysisResult(repository=repo_info)
    
    assert result.provider_versions == {}