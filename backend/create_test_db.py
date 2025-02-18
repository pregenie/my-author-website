#!/usr/bin/env python
from main import app, db
from backend.config import TestingConfig

# Set the testing configuration (which uses an in-memory SQLite DB)
app.config.from_object(TestingConfig)

with app.app_context():
    # Create all database tables
    db.create_all()
    print("In-memory SQLite test database created successfully.")

