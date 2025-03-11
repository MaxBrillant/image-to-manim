#!/bin/bash

# Install dependencies if needed
pip install -r requirements.txt

# Start the application with Gunicorn
# 4 worker processes, binding to all interfaces on port 5000
gunicorn --workers=4 --bind=0.0.0.0:5000 wsgi:app 