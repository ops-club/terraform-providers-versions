import pytest
from terraform_analyzer.models.repository import RepositoryInfo, AnalysisResult
from terraform_analyzer.formatters.output_formatter import TextFormatter, JsonFormatter, CsvFormatter, FormatterFactory

@pytest.fixture
def sample_results():
    """Fixture pour créer des résultats de test."""
    repo1 = RepositoryInfo(
        name="test-repo-1",
        repository="https://github.com/test/repo1",
        terraform_path="terraform"
    )
    repo2 = RepositoryInfo(
        name="test-repo-2",
        repository="https://github.com/test/repo2",
        terraform_path="terraform"
    )
    
    return [
        AnalysisResult(
            repository=repo1,
            terraform_version="1.0.0",
            provider_versions={"aws": "4.0.0"}
        ),
        AnalysisResult(
            repository=repo2,
            error="Test error"
        )
    ]

def test_text_formatter(sample_results):
    """Test le formatage en texte."""
    formatter = TextFormatter()
    output = formatter.format(sample_results)
    
    assert "test-repo-1" in output
    assert "1.0.0" in output
    assert "aws" in output
    assert "4.0.0" in output
    assert "test-repo-2" in output
    assert "Test error" in output

def test_json_formatter(sample_results):
    """Test le formatage en JSON."""
    formatter = JsonFormatter()
    output = formatter.format(sample_results)
    
    import json
    data = json.loads(output)
    
    assert len(data) == 2
    assert data[0]["repository"]["name"] == "test-repo-1"
    assert data[0]["terraform_version"] == "1.0.0"
    assert data[0]["provider_versions"]["aws"] == "4.0.0"
    assert data[1]["repository"]["name"] == "test-repo-2"
    assert data[1]["error"] == "Test error"

def test_csv_formatter(sample_results):
    """Test le formatage en CSV."""
    formatter = CsvFormatter()
    output = formatter.format(sample_results)
    
    lines = output.split("\n")
    assert len(lines) == 3  # Header + 2 results
    
    # Vérifier l'en-tête
    header = lines[0].split(",")
    assert "Repository Name" in header
    assert "Terraform Version" in header
    assert "Provider Versions" in header
    assert "Error" in header

def test_formatter_factory():
    """Test la factory des formateurs."""
    assert isinstance(FormatterFactory.get_formatter("text"), TextFormatter)
    assert isinstance(FormatterFactory.get_formatter("json"), JsonFormatter)
    assert isinstance(FormatterFactory.get_formatter("csv"), CsvFormatter)
    
    with pytest.raises(ValueError):
        FormatterFactory.get_formatter("invalid") 