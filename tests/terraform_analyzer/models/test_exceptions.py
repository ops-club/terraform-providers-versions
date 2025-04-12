import pytest
from terraform_analyzer.models.exceptions import RepositoryAnalysisError, TerraformAnalysisError

def test_repository_analysis_error():
    """Test la création et le message d'une RepositoryAnalysisError."""
    error_message = "Test repository error"
    error = RepositoryAnalysisError(error_message)
    
    assert str(error) == error_message
    assert isinstance(error, Exception)

def test_terraform_analysis_error():
    """Test la création et le message d'une TerraformAnalysisError."""
    error_message = "Test terraform error"
    error = TerraformAnalysisError(error_message)
    
    assert str(error) == error_message
    assert isinstance(error, Exception) 