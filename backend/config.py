import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:postgres@localhost/my_author_website_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestingConfig(Config):
    TESTING = True
    # Use an in-memory SQLite database for testing to ensure tests run quickly and don't affect production data.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
