# AegisPay Multi-Agent Fraud Defense System for PayPal Commerce
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications
COPY aegispay-system/orchestrator_agent/requirements.txt /app/requirements.txt

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY aegispay-system/ /app/aegispay-system/
COPY dashboard/ /app/dashboard/

# Expose primary port
EXPOSE 8080

# Default entrypoint
CMD ["python", "aegispay-system/orchestrator_agent/agent.py"]
