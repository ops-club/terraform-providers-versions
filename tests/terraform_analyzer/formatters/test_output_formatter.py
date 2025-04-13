import pytest
from terraform_analyzer.models.repository import RepositoryInfo, ProviderVersion, AnalysisResult
from terraform_analyzer.formatters.output_formatter import TextFormatter, JsonFormatter, CsvFormatter, FormatterFactory

@pytest.fixture
def repo_info():
    return RepositoryInfo(
        name="test-repo",
        repository="https://github.com/test/test-repo",
        terraform_path="terraform",
        branch="main"
    )

@pytest.fixture
def provider_version():
    return ProviderVersion(
        current_version="3.0.0",
        latest_version="4.0.0"
    )

@pytest.fixture
def sample_results(repo_info, provider_version):
    return [
        AnalysisResult(
            repository=repo_info,
            terraform_version="1.0.0",
            provider_versions={"aws": provider_version}
        )
    ]

def test_text_formatter(sample_results):
    """Test le formateur de texte."""
    formatter = FormatterFactory.get_formatter("text")
    output = formatter.format(sample_results)
    assert "test-repo" in output
    assert "1.0.0" in output
    assert "aws" in output
    assert "3.0.0" in output
    assert "4.0.0" in output

def test_json_formatter(sample_results):
    """Test le formateur JSON."""
    formatter = FormatterFactory.get_formatter("json")
    output = formatter.format(sample_results)
    assert "test-repo" in output
    assert "1.0.0" in output
    assert "aws" in output
    assert "3.0.0" in output
    assert "4.0.0" in output

def test_csv_formatter(sample_results):
    """Test le formateur CSV."""
    formatter = FormatterFactory.get_formatter("csv")
    output = formatter.format(sample_results)
    assert "test-repo" in output
    assert "1.0.0" in output
    assert "aws" in output
    assert "3.0.0" in output
    assert "4.0.0" in output

def test_formatter_factory():
    """Test la création des formateurs."""
    text_formatter = FormatterFactory.get_formatter("text")
    json_formatter = FormatterFactory.get_formatter("json")
    csv_formatter = FormatterFactory.get_formatter("csv")
    html_formatter = FormatterFactory.get_formatter("html")
    markdown_formatter = FormatterFactory.get_formatter("markdown")
    
    assert str(text_formatter.__class__.__name__) == "TextFormatter"
    assert str(json_formatter.__class__.__name__) == "JsonFormatter"
    assert str(csv_formatter.__class__.__name__) == "CsvFormatter"
    assert str(html_formatter.__class__.__name__) == "HtmlFormatter"
    assert str(markdown_formatter.__class__.__name__) == "MarkdownFormatter"