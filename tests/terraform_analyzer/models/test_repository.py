import pytest
from terraform_analyzer.models.repository import RepositoryInfo, AnalysisResult

def test_repository_info_creation():
    """Test la création d'un RepositoryInfo avec tous les paramètres."""
    repo = RepositoryInfo(
        name="test-repo",
        repository="https://github.com/test/test-repo",
        terraform_path="terraform",
        branch="main"
    )
    
    assert repo.name == "test-repo"
    assert repo.repository == "https://github.com/test/test-repo"
    assert repo.terraform_path == "terraform"
    assert repo.branch == "main"

def test_repository_info_creation_without_branch():
    """Test la création d'un RepositoryInfo sans branche spécifiée."""
    repo = RepositoryInfo(
        name="test-repo",
        repository="https://github.com/test/test-repo",
        terraform_path="terraform"
    )
    
    assert repo.name == "test-repo"
    assert repo.repository == "https://github.com/test/test-repo"
    assert repo.terraform_path == "terraform"
    assert repo.branch is None

def test_analysis_result_creation():
    """Test la création d'un AnalysisResult avec tous les paramètres."""
    repo = RepositoryInfo(
        name="test-repo",
        repository="https://github.com/test/test-repo",
        terraform_path="terraform"
    )
    
    result = AnalysisResult(
        repository=repo,
        terraform_version="1.0.0",
        provider_versions={"aws": "4.0.0"},
        error=None
    )
    
    assert result.repository == repo
    assert result.terraform_version == "1.0.0"
    assert result.provider_versions == {"aws": "4.0.0"}
    assert result.error is None

def test_analysis_result_creation_with_error():
    """Test la création d'un AnalysisResult avec une erreur."""
    repo = RepositoryInfo(
        name="test-repo",
        repository="https://github.com/test/test-repo",
        terraform_path="terraform"
    )
    
    result = AnalysisResult(
        repository=repo,
        error="Test error"
    )
    
    assert result.repository == repo
    assert result.terraform_version is None
    assert result.provider_versions == {}
    assert result.error == "Test error"

def test_analysis_result_default_provider_versions():
    """Test que provider_versions est initialisé comme un dictionnaire vide par défaut."""
    repo = RepositoryInfo(
        name="test-repo",
        repository="https://github.com/test/test-repo",
        terraform_path="terraform"
    )
    
    result = AnalysisResult(repository=repo)
    
    assert result.provider_versions == {} 