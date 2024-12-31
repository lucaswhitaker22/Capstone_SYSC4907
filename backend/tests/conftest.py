# tests/conftest.py
import pytest
from app import create_app, db
import warnings
from sqlalchemy import exc as sa_exc
from app.models import Course, Program, ProgramRequirement

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def ignore_warnings():
    warnings.simplefilter("ignore", category=sa_exc.LegacyAPIWarning)
