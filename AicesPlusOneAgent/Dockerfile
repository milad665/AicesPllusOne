# Stage 1: Build React UI
FROM node:18-alpine AS ui-builder

WORKDIR /app/ui

# Copy package files
COPY ui/package.json ui/package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy UI source
COPY ui/ .

# Build for production
RUN npm run build

# Stage 2: Python Runtime
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies
COPY requirements.txt .

# Install dependencies (add google-cloud-run specific if needed later)
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY src/ src/
RUN mkdir -p data
COPY *.py ./
COPY entrypoint.sh .

# Copy built UI from Stage 1
# We'll serve this from FastAPI's StaticFiles
# Assuming src/api.py is configured to serve static files from /app/static or similar
# For now, we copy to /app/ui/dist and update api.py if needed
COPY --from=ui-builder /app/ui/dist /app/ui/dist

# Expose ports
# 8001 for FastAPI/UI
EXPOSE 8001

# Set permissions
RUN chmod +x entrypoint.sh

# Environment variables
ENV GOOGLE_API_KEY=""
ENV STORAGE_TYPE="local"

# Entrypoint
CMD ["./entrypoint.sh"]
