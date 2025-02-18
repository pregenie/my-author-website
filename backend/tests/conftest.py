# tests/conftest.py
import pytest
from app import app, db

@pytest.fixture
def client():
    app.config.from_object('config.TestingConfig')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()
