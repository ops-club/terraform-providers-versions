FROM python:3.10-slim-bullseye

ARG TERRAFORM_VERSION=1.10.3

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

COPY src/ /app/src/
COPY setup.py /app/
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e .

RUN mkdir -p /app/data /app/output

ENV TERRAFORM_HISTORY_FILE=/app/data/terraform_history.json
ENV OUTPUT_DIR=/app/output
ENV TERRAFORM_VERSION=${TERRAFORM_VERSION}
ENV PYTHONPATH=/app

RUN echo '#!/bin/bash\npython3 -m terraform_analyzer.main "$@"' > /usr/local/bin/terraform-analyzer \
    && chmod +x /usr/local/bin/terraform-analyzer

ENTRYPOINT ["terraform-analyzer"]
