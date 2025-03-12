FROM python:3.10-slim

# Install system dependencies for Manim
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
CMD gunicorn --bind 0.0.0.0:8000 --workers 1 --threads 2 --timeout 600 app:app
