FROM python:3.10-slim

# Install system dependencies for Manim
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    texlive \
    texlive-latex-extra \
    texlive-fonts-extra \
    texlive-latex-recommended \
    texlive-science \
    tipa \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    sox \
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
CMD gunicorn --bind 0.0.0.0:8000 app:app
