# QFS V13 Deterministic Build Environment
# Ensures reproducible builds across all environments

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy source code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash qfsuser
USER qfsuser

# Set environment variables for deterministic behavior
ENV PYTHONHASHSEED=0
ENV PYTHONDONTWRITEBYTECODE=1

# Default command
CMD ["python", "src/libs/CertifiedMath.py"]