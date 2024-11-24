#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Make migrations (create migration files if needed)
python manage.py makemigrations

# Apply any outstanding database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input
