# Terraform Version Analyzer

This Python application allows you to analyze Terraform and provider versions used in different Git repositories. It can track version changes over time and output results in multiple formats.

## Prerequisites

- Python 3.8 or higher
- Git installed on your system
- `just` installed on your system
- Terraform installed on your system

## Installation

1. Clone this repository
2. Install dependencies with just:
```bash
just setup
```

## Configuration

Create a `config.yaml` file with the following structure:

```yaml
repos:
- name: repo-name
  repository: https://github.com/user/repo
  terraform-path: path/to/terraform
  branch: main  # Optional, defaults to repository's default branch
```

Configuration options:
- `name`: Repository name (used for temporary cloning)
- `repository`: Git repository URL (supports HTTPS and SSH)
- `terraform-path`: Relative path to the directory containing Terraform files
- `branch`: Specific branch to analyze (optional)

## Usage

### Command Line

Basic usage:
```bash
just run              # Run with text output (default)
just run-json         # Run with JSON output
just run-csv          # Run with CSV output
just run-html         # Run with HTML output
just run-md           # Run with Markdown output
```

Save output to a file:
```bash
just save-output <format> <filename>  # e.g., just save-output json results.json
just save-html <filename>             # Save HTML output to a file
just save-md <filename>               # Save Markdown output to a file
```

History and version tracking:
```bash
just show-history     # Show version history for all repositories
just show-changes     # Show version changes between runs
```

Development commands:
```bash
just activate         # Activate virtual environment
just test            # Run tests
just test-cov        # Run tests with coverage
just clean           # Clean virtual environment and history
```

### Docker Support

Build and run with Docker:
```bash
just docker-build            # Build Docker image
just docker-run             # Run with text output
just docker-run-json        # Run with JSON output
just docker-run-csv         # Run with CSV output
```

When using Docker, mount your configuration and output directories:
- Config file: `-v $(pwd)/config.yaml:/app/config.yaml`
- Output directory: `-v $(pwd)/output:/app/output`

## Output Formats

The analyzer supports five output formats:

1. Text (default): Human-readable format
2. JSON: Structured data format for programmatic use
3. CSV: Tabular format for spreadsheet analysis
4. HTML: Rich web-based format with styling and visual indicators
5. Markdown: Documentation-friendly format suitable for version control

Each format has specific advantages:
- **Text**: Best for direct console viewing
- **JSON**: Ideal for API integration and automated processing
- **CSV**: Perfect for importing into Excel or data analysis tools
- **HTML**: Great for sharing reports via web browsers, includes styling and visual indicators
- **Markdown**: Excellent for documentation, GitHub wikis, and version-controlled reports

## Version History

The tool maintains a history of Terraform and provider versions in `terraform_history.json`. This allows you to:
- Track version changes over time
- Compare versions between runs
- Identify when and how versions were updated

## Features

The analyzer will:
1. Clone each repository in a temporary directory
2. Use Terraform CLI to analyze:
   - Required Terraform version
   - Provider versions used
3. Track version changes over time
4. Support multiple output formats
5. Clean up temporary directories

## Development

The project uses:
- pytest for testing (`just test`)
- Coverage reporting (`just test-cov`)
- Docker for containerized execution
- GitHub Actions for CI/CD