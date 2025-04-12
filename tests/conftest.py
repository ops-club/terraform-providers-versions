import pytest
from terraform_analyzer.models.repository import RepositoryInfo, AnalysisResult

@pytest.fixture
def repo_info():
    """Fixture partagé pour créer un RepositoryInfo de test."""
    return RepositoryInfo(
        name="test-repo",
        repository="https://github.com/test/test-repo",
        terraform_path="terraform",
        branch="main"
    )

@pytest.fixture
def analysis_result(repo_info):
    """Fixture partagé pour créer un AnalysisResult de test."""
    return AnalysisResult(
        repository=repo_info,
        terraform_version="1.0.0",
        provider_versions={"aws": "4.0.0"},
        error=None
    ) 