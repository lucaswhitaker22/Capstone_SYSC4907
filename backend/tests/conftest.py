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

@pytest.fixture
def sample_course():
    return {
        'course_id': 'CS101',
        'course_name': 'Introduction to Programming',
        'credits': 3.0
    }

@pytest.fixture
def sample_program():
    return {
        'program_id': 'SENG',
        'program_name': 'Software Engineering',
        'total_enrollment': 100,
        'blocks_20_count': 5,
        'blocks_10_count': 2
    }

@pytest.fixture
def sample_requirement():
    return {
        'program_id': 'SENG',
        'course_id': 'CS101',
        'term': '1'
    }

@pytest.fixture
def sample_block():
    return {
        'block_id': 'BLK1',
        'program_id': 'SENG',
        'block_size': 20,
        'term': '1',
        'academic_year': '2024-25',
        'schedule_rating': None,
        'status': 'DRAFT'
    }

@pytest.fixture
def sample_block_schedule():
    return {
        'block_id': 'BLK1',
        'offering_id': 1,
        'course_id': 'CS101',
        'section_type': 'LEC',
        'section_code': 'A',
        'day_of_week': 1,
        'start_time': '08:30',
        'end_time': '10:00'
    }


@pytest.fixture(autouse=True)
def ignore_warnings():
    warnings.simplefilter("ignore", category=sa_exc.LegacyAPIWarning)
