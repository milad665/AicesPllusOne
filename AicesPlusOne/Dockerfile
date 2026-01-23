# AicesPlusOne Code Analyzer Dockerfile
FROM python:3.11-slim

# Set environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
# git: for cloning repos
# build-essential, python3-dev: for building python packages (if needed)
# curl: for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files
COPY requirements.txt .
COPY setup.py .

# Install dependencies (including dev deps if needed for testing, but mostly prod)
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -e .

# Copy application code
COPY . .

# Create directory for repositories
RUN mkdir -p repositories

# Expose API port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the FastAPI app
# Uses uvicorn to serve the app
CMD ["uvicorn", "aices_plus_one.main:app", "--host", "0.0.0.0", "--port", "8000"]
