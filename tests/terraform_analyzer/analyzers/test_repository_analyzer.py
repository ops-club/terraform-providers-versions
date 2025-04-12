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
        mock.analyze_directory.return_value = ("1.0.0", {"aws": {"current_version": "3.0.0", "latest_version": "4.0.0"}})
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
    assert analyzer.repository == repo_info
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
            analyzer.repo_path,
            branch=repo_info.branch
        )

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
            analyzer.repo_path,
            branch=None
        )

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
    expected_path = os.path.join("/tmp/test-repo", repo_info.terraform_path)
    
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = True
        path = analyzer._verify_terraform_path()
        assert path == expected_path
        
        mock_exists.return_value = False
        with pytest.raises(RepositoryAnalysisError):
            analyzer._verify_terraform_path()

def test_repository_analyzer_analyze_success(repo_info):
    """Test l'analyse réussie d'un dépôt."""
    with RepositoryAnalyzer(repo_info) as analyzer:
        with patch('terraform_analyzer.analyzers.repository_analyzer.git.Repo') as mock_git_repo, \
             patch('terraform_analyzer.analyzers.repository_analyzer.TerraformAnalyzer') as mock_terraform:
            # Mock git clone
            mock_repo = MagicMock()
            mock_git_repo.clone_from.return_value = mock_repo
            
            # Mock terraform analysis
            mock_terraform.analyze_directory.return_value = ("1.0.0", {"aws": {"current_version": "3.0.0", "latest_version": "4.0.0"}})
            
            with patch('os.path.exists') as mock_exists:
                mock_exists.return_value = True
                result = analyzer.analyze()
                
                assert result.repository == repo_info
                assert result.terraform_version == "1.0.0"
                assert "aws" in result.provider_versions
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
        assert "Analysis failed" in result.error

def test_repository_analyzer_with_config(config_repo_info):
    """Test repository analyzer using configuration from file."""
    with RepositoryAnalyzer(config_repo_info) as analyzer:
        with patch('terraform_analyzer.analyzers.repository_analyzer.git.Repo') as mock_git_repo, \
             patch('terraform_analyzer.analyzers.repository_analyzer.TerraformAnalyzer') as mock_terraform:
            # Mock git clone
            mock_repo = MagicMock()
            mock_git_repo.clone_from.return_value = mock_repo
            
            # Mock terraform analysis
            mock_terraform.analyze_directory.return_value = ("1.0.0", {"aws": {"current_version": "3.0.0", "latest_version": "4.0.0"}})
            
            with patch('os.path.exists') as mock_exists:
                mock_exists.return_value = True
                result = analyzer.analyze()
                
                assert result.repository == config_repo_info
                assert result.terraform_version == "1.0.0"
                assert "aws" in result.provider_versions
                assert result.error is None
                mock_git_repo.clone_from.assert_called_once_with(
                    config_repo_info.repository,
                    analyzer.repo_path,
                    branch=config_repo_info.branch
                )