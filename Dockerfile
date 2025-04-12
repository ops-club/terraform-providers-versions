FROM python:3.13-slim

# Install Terraform
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LO https://releases.hashicorp.com/terraform/1.10.3/terraform_1.10.3_linux_amd64.zip \
    && unzip terraform_1.10.3_linux_amd64.zip \
    && mv terraform /usr/local/bin/ \
    && rm terraform_1.10.3_linux_amd64.zip

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY setup.py .

# Install the package
RUN pip install -e .

# Create directories for data
RUN mkdir -p /app/data /app/output

# Set environment variables
ENV PYTHONPATH=/app/src
ENV TERRAFORM_HISTORY_FILE=/app/data/terraform_history.json
ENV OUTPUT_DIR=/app/output

ENTRYPOINT ["python", "-m", "terraform_analyzer.main"]