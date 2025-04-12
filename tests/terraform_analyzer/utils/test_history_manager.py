import pytest
from datetime import datetime
from terraform_analyzer.models.repository import RepositoryInfo, AnalysisResult, ProviderVersion
from terraform_analyzer.models.history import HistoryEntry, VersionChange
from terraform_analyzer.utils.history_manager import HistoryManager

@pytest.fixture
def sample_repository(test_config):
    repo = test_config['test_repositories'][0]
    return RepositoryInfo(
        name=repo['name'],
        repository=repo['repository'],
        terraform_path=repo['terraform-path'],
        branch=repo['branch']
    )

@pytest.fixture
def history_manager(tmp_path):
    return HistoryManager(tmp_path / "test_history.json")

def test_history_manager_initialization(history_manager):
    """Test that history manager initializes with empty dict"""
    assert isinstance(history_manager.history, dict)

def test_add_entry_with_latest_versions(history_manager, sample_repository):
    """Test adding and retrieving an entry with both current and latest versions"""
    result = AnalysisResult(
        repository=sample_repository,
        terraform_version="1.5.0",
        provider_versions={
            "registry.terraform.io/hashicorp/aws": ProviderVersion(
                current_version="4.0.0",
                latest_version="5.0.0"
            )
        },
        error=None
    )
    
    history_manager.add_entry(result)
    
    history = history_manager.get_repository_history(sample_repository.name)
    assert history is not None
    assert history.terraform_version == "1.5.0"
    assert "registry.terraform.io/hashicorp/aws" in history.provider_versions
    
    provider_version = history.provider_versions["registry.terraform.io/hashicorp/aws"]
    assert provider_version.current_version == "4.0.0"
    assert provider_version.latest_version == "5.0.0"

def test_version_changes_detection(history_manager, sample_repository):
    """Test detection of version changes between entries"""
    # Add first entry
    old_result = AnalysisResult(
        repository=sample_repository,
        terraform_version="1.5.0",
        provider_versions={
            "registry.terraform.io/hashicorp/aws": ProviderVersion(
                current_version="4.0.0",
                latest_version="5.0.0"
            )
        },
        error=None
    )
    history_manager.add_entry(old_result)
    
    # Add second entry with updated version
    new_result = AnalysisResult(
        repository=sample_repository,
        terraform_version="1.5.0",
        provider_versions={
            "registry.terraform.io/hashicorp/aws": ProviderVersion(
                current_version="4.1.0",
                latest_version="5.0.0"
            )
        },
        error=None
    )
    history_manager.add_entry(new_result)
    
    changes = history_manager.get_version_changes(sample_repository.name)
    assert len(changes) == 1
    
    change = changes[0]
    assert change.provider == "registry.terraform.io/hashicorp/aws"
    assert change.old_version.current_version == "4.0.0"
    assert change.old_version.latest_version == "5.0.0"
    assert change.new_version.current_version == "4.1.0"
    assert change.new_version.latest_version == "5.0.0"
    assert change.is_upgrade_available  # Should be True since latest is 5.0.0

def test_no_changes_when_versions_same(history_manager, sample_repository):
    """Test that no changes are detected when versions are identical"""
    result = AnalysisResult(
        repository=sample_repository,
        terraform_version="1.5.0",
        provider_versions={
            "registry.terraform.io/hashicorp/aws": ProviderVersion(
                current_version="4.0.0",
                latest_version="5.0.0"
            )
        },
        error=None
    )
    
    history_manager.add_entry(result)
    history_manager.add_entry(result)
    
    changes = history_manager.get_version_changes(sample_repository.name)
    assert len(changes) == 0

def test_error_handling(history_manager, sample_repository):
    """Test that error results are handled correctly"""
    error_result = AnalysisResult(
        repository=sample_repository,
        terraform_version=None,
        provider_versions={},
        error="Test error"
    )
    
    history_manager.add_entry(error_result)
    history = history_manager.get_repository_history(sample_repository.name)
    assert history is None