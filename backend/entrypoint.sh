#!/bin/bash
set -e

# --- (Optional) If using a combined container with PostgreSQL initialization ---
# For a separated system, you do not need to initialize or alter PostgreSQL here.
#
# If you previously had PostgreSQL initialization commands here, remove them.
#
# -------------------------------------------------------------

# Wait for the PostgreSQL container (or service) to be available.
echo "Waiting for PostgreSQL to be available..."
sleep 10

# Set the FLASK_APP environment variable so that the Flask CLI can find your application.
export FLASK_APP=main.py

echo "Running database creation script..."
python create_db.py

echo "Applying database migrations..."
# Use the Flask CLI with the FLASK_APP set; if needed, you can also explicitly specify --app.
flask db upgrade

echo "Seeding the database..."
python seed_db.py

echo "Starting the Flask application..."
python main.py
