import os
import json
import pytest
from unittest.mock import patch, MagicMock
from terraform_analyzer.analyzers.terraform_analyzer import TerraformAnalyzer
from terraform_analyzer.models.exceptions import TerraformAnalysisError

@pytest.fixture
def terraform_dir(tmp_path):
    """Create a test Terraform directory."""
    terraform_dir = tmp_path / "terraform"
    terraform_dir.mkdir()
    
    # Create a versions.tf file
    versions_file = terraform_dir / "versions.tf"
    versions_file.write_text("""
terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}
""")
    
    return terraform_dir

def mock_terraform_command(mocker, stdout="", stderr="", returncode=0):
    """Helper to mock terraform command responses"""
    mock_run = mocker.patch('subprocess.run')
    mock_run.return_value = MagicMock(
        stdout=stdout,
        stderr=stderr,
        returncode=returncode
    )
    return mock_run

@pytest.fixture
def mock_terraform_version(mocker):
    """Mock terraform version command response"""
    version_output = {
        "terraform_version": "1.0.0",
        "provider_selections": {
            "registry.terraform.io/hashicorp/aws": "4.0.0",
            "registry.terraform.io/hashicorp/azurerm": "3.0.0"
        }
    }
    return mock_terraform_command(mocker, stdout=json.dumps(version_output), returncode=0)

def test_analyze_directory(terraform_dir, mock_terraform_version):
    """Test analyzing a valid Terraform directory."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"versions": [{"version": "4.1.0"}]}
        mock_get.return_value = mock_response
        
        terraform_version, provider_versions = TerraformAnalyzer.analyze_directory(str(terraform_dir))
        
        assert terraform_version is not None
        assert "registry.terraform.io/hashicorp/aws" in provider_versions
        assert "registry.terraform.io/hashicorp/azurerm" in provider_versions

def test_analyze_directory_error(terraform_dir, mocker):
    """Test analyzing a directory with terraform errors."""
    mock_terraform_command(mocker, stderr="Error initializing", returncode=1)
    
    with pytest.raises(TerraformAnalysisError):
        TerraformAnalyzer.analyze_directory(str(terraform_dir))

def test_is_prerelease_detection():
    """Test the detection of prerelease versions"""
    assert TerraformAnalyzer._is_prerelease("1.0.0-alpha") == True
    assert TerraformAnalyzer._is_prerelease("2.0.0-beta.1") == True
    assert TerraformAnalyzer._is_prerelease("3.0.0-rc1") == True
    assert TerraformAnalyzer._is_prerelease("1.0.0") == False
    assert TerraformAnalyzer._is_prerelease("2.1.5") == False

def test_get_latest_provider_versions_without_prerelease():
    """Test that prerelease versions are excluded by default"""
    mock_versions = {
        "versions": [
            {"version": "1.0.0"},
            {"version": "1.1.0-alpha"},
            {"version": "1.0.1"},
            {"version": "1.1.0-beta"},
            {"version": "1.0.2"}
        ]
    }
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_versions
        mock_get.return_value = mock_response
        
        TerraformAnalyzer.set_include_prerelease(False)
        latest_versions = TerraformAnalyzer._get_latest_provider_versions({
            "registry.terraform.io/hashicorp/test": "1.0.0"
        })
        
        assert latest_versions["registry.terraform.io/hashicorp/test"] == "1.0.2"

def test_get_latest_provider_versions_with_prerelease():
    """Test that prerelease versions are included when flag is set"""
    mock_versions = {
        "versions": [
            {"version": "1.0.0"},
            {"version": "1.1.0-alpha"},
            {"version": "1.0.1"},
            {"version": "1.1.0-beta"},
            {"version": "1.0.2"}
        ]
    }
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_versions
        mock_get.return_value = mock_response
        
        TerraformAnalyzer.set_include_prerelease(True)
        latest_versions = TerraformAnalyzer._get_latest_provider_versions({
            "registry.terraform.io/hashicorp/test": "1.0.0"
        })
        
        assert latest_versions["registry.terraform.io/hashicorp/test"] == "1.1.0-beta"