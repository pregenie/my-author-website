#!/bin/bash
set -e

echo "Waiting for PostgreSQL to start..."

# Wait until PostgreSQL is reachable (uses the container name 'db' from docker-compose)
while ! nc -z db 5432; do
  sleep 1
done

echo "PostgreSQL is up and running."

# Run the script to check/create the database
python create_db.py

# Apply any pending migrations (Flask-Migrate)
flask db upgrade

# Finally, start the Flask application
python app.py
