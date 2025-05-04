# Build stage
FROM python:3.13-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    git \
    binutils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pyinstaller==6.13.0

# Copy application code
COPY src/ ./src/
COPY setup.py .
COPY terraform_analyzer.spec .

# Build binary
RUN pyinstaller terraform_analyzer.spec --clean --noconfirm

# Runtime stage
FROM debian:bookworm-slim

# Define Terraform version argument with a default value
ARG TERRAFORM_VERSION=1.10.3

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LO https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    && unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    && mv terraform /usr/local/bin/ \
    && rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip

WORKDIR /app

# Copy the binary from builder
COPY --from=builder /app/dist/terraform-analyzer /usr/local/bin/

# Create data directory
RUN mkdir -p /app/data /app/output

# Set environment variables
ENV TERRAFORM_HISTORY_FILE=/app/data/terraform_history.json
ENV OUTPUT_DIR=/app/output
ENV TERRAFORM_VERSION=${TERRAFORM_VERSION}

ENTRYPOINT ["terraform-analyzer"]