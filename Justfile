# Help
default:
    @just --list 
    
# Create virtual environment and install dependencies
setup:
    python -m venv .venv
    . .venv/bin/activate && pip install -r requirements.txt

# Activate virtual environment
activate:
    . .venv/bin/activate

# Run the application with text output (default)
run:
    PYTHONPATH=src python src/terraform_analyzer/main.py

# Run with JSON output
run-json:
    PYTHONPATH=src python src/terraform_analyzer/main.py --output-format json

# Run with CSV output
run-csv:
    PYTHONPATH=src python src/terraform_analyzer/main.py --output-format csv

# Run with HTML output
run-html:
    PYTHONPATH=src python src/terraform_analyzer/main.py --output-format html

# Run with Markdown output
run-md:
    PYTHONPATH=src python src/terraform_analyzer/main.py --output-format markdown

# Run and save output to a file (usage: just save-output json results.json)
save-output format output_file:
    PYTHONPATH=src python src/terraform_analyzer/main.py --output-format {{format}} > {{output_file}}

# Save HTML output to a file
save-html output_file:
    PYTHONPATH=src python src/terraform_analyzer/main.py --output-format html --output-file {{output_file}}

# Save Markdown output to a file
save-md output_file:
    PYTHONPATH=src python src/terraform_analyzer/main.py --output-format markdown --output-file {{output_file}}

# Run tests
test:
    PYTHONPATH=src pytest

# Run tests with coverage
test-cov:
    PYTHONPATH=src pytest --cov=terraform_analyzer

# Show history for all repositories
show-history:
    PYTHONPATH=src python src/terraform_analyzer/main.py --show-history

# Show version changes for all repositories
show-changes:
    PYTHONPATH=src python src/terraform_analyzer/main.py --show-changes

# Clean virtual environment and history
clean:
    rm -rf .venv
    rm -f terraform_history.json

# Build Docker image
docker-build:
    docker build -t terraform-analyzer .

# Run the application in Docker
docker-run:
    docker run -v $(pwd)/config.yaml:/app/config.yaml -v $(pwd)/output:/app/output terraform-analyzer

# Run with specific format in Docker (usage: just docker-run-format html)
docker-run-format format:
    docker run -v $(pwd)/config.yaml:/app/config.yaml -v $(pwd)/output:/app/output terraform-analyzer --output-format {{format}}
