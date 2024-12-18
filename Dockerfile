# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Required for video processing
    ffmpeg \
    # Required for moviepy
    python3-dev \
    python3-numpy \
    # Required for building Python packages
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m appuser && \
    mkdir -p downloads && \
    chown -R appuser:appuser /app downloads

# Copy and install requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Copy application files
COPY clipcutter.py .env.example ./
RUN cp .env.example .env

# Command to run the application
CMD ["python", "clipcutter.py"]
