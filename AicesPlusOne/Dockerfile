FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY aices_plus_one/ ./aices_plus_one/
COPY setup.py ./

# Create necessary directories
RUN mkdir -p /app/repositories /app/data

# Set environment variables
ENV PYTHONPATH=/app
ENV DATABASE_PATH=/app/data/repositories.db
ENV REPOSITORIES_DIR=/app/repositories
ENV SSH_KEYS_DIR=/tmp/git_ssh_keys

# Default port (Cloud Run will override this with PORT=8080)
ENV PORT=8000

# Expose port (Cloud Run will use PORT env var)
EXPOSE $PORT

# Health check - use PORT env var
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests, os; requests.get(f'http://localhost:{os.getenv(\"PORT\", \"8000\")}/health')" || exit 1

# Run the application
CMD ["python", "-m", "aices_plus_one.main"]
