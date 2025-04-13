import os
import yaml
import pytest
from unittest.mock import patch, MagicMock
from terraform_analyzer.models.repository import RepositoryInfo
from terraform_analyzer.models.exceptions import RepositoryAnalysisError
from terraform_analyzer.analyzers.repository_analyzer import RepositoryAnalyzer

@pytest.fixture
def repo_info(test_config):
    """Fixture pour créer un RepositoryInfo de test."""
    repo = test_config['test_repositories'][0]
    return RepositoryInfo(
        name=repo['name'],
        repository=repo['repository'],
        terraform_path=repo['terraform-path'],
        branch=repo['branch']
    )

@pytest.fixture
def mock_terraform_analyzer():
    """Fixture pour mocker l'analyseur Terraform."""
    with patch('terraform_analyzer.analyzers.repository_analyzer.TerraformAnalyzer') as mock:
        analyzer = MagicMock()
        analyzer.analyze_terraform_dir.return_value = ("1.0.0", {"aws": "4.0.0"})
        mock.return_value = analyzer
        yield mock

@pytest.fixture
def test_config():
    """Load test configuration from YAML file."""
    config_path = os.path.join(os.path.dirname(__file__), "../../config/test_config.yaml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

@pytest.fixture
def config_repo_info(test_config):
    """Create RepositoryInfo from test config."""
    repo = test_config['test_repositories'][0]
    return RepositoryInfo(
        name=repo['name'],
        repository=repo['repository'],
        terraform_path=repo['terraform-path'],
        branch=repo.get('branch')
    )

def test_repository_analyzer_initialization(repo_info):
    """Test l'initialisation de l'analyseur de dépôt."""
    analyzer = RepositoryAnalyzer(repo_info)
    assert analyzer.repo_info == repo_info
    assert analyzer.temp_dir is None
    assert analyzer.repo_path is None

@patch('terraform_analyzer.analyzers.repository_analyzer.git.Repo')
def test_repository_analyzer_clone_success(mock_git_repo, repo_info):
    """Test le clonage réussi d'un dépôt."""
    mock_repo = MagicMock()
    mock_git_repo.clone_from.return_value = mock_repo
    
    analyzer = RepositoryAnalyzer(repo_info)
    with analyzer:
        analyzer._clone_repository()
        
        mock_git_repo.clone_from.assert_called_once_with(
            repo_info.repository,
            analyzer.repo_path
        )
        mock_repo.git.checkout.assert_called_once_with(repo_info.branch)

@patch('terraform_analyzer.analyzers.repository_analyzer.git.Repo')
def test_repository_analyzer_clone_without_branch(mock_git_repo, repo_info):
    """Test le clonage d'un dépôt sans branche spécifiée."""
    repo_info.branch = None
    mock_repo = MagicMock()
    mock_git_repo.clone_from.return_value = mock_repo
    
    analyzer = RepositoryAnalyzer(repo_info)
    with analyzer:
        analyzer._clone_repository()
        
        mock_git_repo.clone_from.assert_called_once_with(
            repo_info.repository,
            analyzer.repo_path
        )
        mock_repo.git.checkout.assert_not_called()

@patch('terraform_analyzer.analyzers.repository_analyzer.git.Repo')
def test_repository_analyzer_clone_error(mock_git_repo, repo_info):
    """Test la gestion des erreurs lors du clonage."""
    mock_git_repo.clone_from.side_effect = Exception("Clone failed")
    
    analyzer = RepositoryAnalyzer(repo_info)
    with analyzer:
        with pytest.raises(RepositoryAnalysisError):
            analyzer._clone_repository()

def test_repository_analyzer_verify_terraform_path(repo_info):
    """Test la vérification du chemin Terraform."""
    analyzer = RepositoryAnalyzer(repo_info)
    analyzer.repo_path = "/tmp/test-repo"
    
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = True
        path = analyzer._get_terraform_path()
        assert path == "/tmp/test-repo/terraform"
        
        mock_exists.return_value = False
        with pytest.raises(RepositoryAnalysisError):
            analyzer._get_terraform_path()

def test_repository_analyzer_analyze_success(repo_info, mock_terraform_analyzer):
    """Test l'analyse réussie d'un dépôt."""
    analyzer = RepositoryAnalyzer(repo_info)
    
    with patch('terraform_analyzer.analyzers.repository_analyzer.git.Repo') as mock_git_repo:
        mock_repo = MagicMock()
        mock_git_repo.clone_from.return_value = mock_repo
        
        result = analyzer.analyze()
        
        assert result.repository == repo_info
        assert result.terraform_version == "1.0.0"
        assert result.provider_versions == {"aws": "4.0.0"}
        assert result.error is None

def test_repository_analyzer_analyze_error(repo_info):
    """Test la gestion des erreurs lors de l'analyse."""
    analyzer = RepositoryAnalyzer(repo_info)
    
    with patch('terraform_analyzer.analyzers.repository_analyzer.git.Repo') as mock_git_repo:
        mock_git_repo.clone_from.side_effect = Exception("Analysis failed")
        
        result = analyzer.analyze()
        
        assert result.repository == repo_info
        assert result.terraform_version is None
        assert result.provider_versions == {}
        assert result.error == "Analysis failed"

def test_repository_analyzer_with_config(config_repo_info, mock_terraform_analyzer):
    """Test repository analyzer using configuration from file."""
    analyzer = RepositoryAnalyzer(config_repo_info)
    
    with patch('terraform_analyzer.analyzers.repository_analyzer.git.Repo') as mock_git_repo:
        mock_repo = MagicMock()
        mock_git_repo.clone_from.return_value = mock_repo
        
        result = analyzer.analyze()
        
        assert result.repository == config_repo_info
        assert result.terraform_version == "1.0.0"
        assert result.provider_versions == {"aws": "4.0.0"}
        assert result.error is None
        mock_git_repo.clone_from.assert_called_once_with(
            config_repo_info.repository,
            analyzer.repo_path
        )
        mock_repo.git.checkout.assert_called_once_with(config_repo_info.branch)