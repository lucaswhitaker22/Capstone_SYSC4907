# tests/test_program_requirements.py
from http import HTTPStatus
from app import db
from app.models import Program, Course, ProgramRequirement

def test_get_program_requirements(client):
    # Create prerequisites
    program = Program(
        program_id='SENG',
        program_name='Software Engineering',
        total_enrollment=100,
        blocks_20_count=5,
        blocks_10_count=2
    )
    course = Course(
        course_id='CS101',
        course_name='Programming',
        credits=3.0
    )
    requirement = ProgramRequirement(
        program_id='SENG',
        course_id='CS101',
        term='1'
    )
    
    db.session.add(program)
    db.session.add(course)
    db.session.add(requirement)
    db.session.commit()
    
    response = client.get('/api/requirements/program/SENG')
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.OK
    assert len(data) == 1
    assert data[0]['program_id'] == 'SENG'
    assert data[0]['course_id'] == 'CS101'
    assert data[0]['term'] == '1'

def test_create_requirement(client):
    # Create prerequisites
    program = Program(
        program_id='SENG',
        program_name='Software Engineering',
        total_enrollment=100,
        blocks_20_count=5,
        blocks_10_count=2
    )
    course = Course(
        course_id='CS101',
        course_name='Programming',
        credits=3.0
    )
    
    db.session.add(program)
    db.session.add(course)
    db.session.commit()
    
    requirement_data = {
        'program_id': 'SENG',
        'course_id': 'CS101',
        'term': '1'
    }
    
    response = client.post('/api/requirements/', json=requirement_data)
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.CREATED
    assert data['program_id'] == requirement_data['program_id']
    assert data['course_id'] == requirement_data['course_id']
    assert data['term'] == requirement_data['term']

def test_create_duplicate_requirement(client):
    # Create prerequisites
    program = Program(
        program_id='SENG',
        program_name='Software Engineering',
        total_enrollment=100,
        blocks_20_count=5,
        blocks_10_count=2
    )
    course = Course(
        course_id='CS101',
        course_name='Programming',
        credits=3.0
    )
    requirement = ProgramRequirement(
        program_id='SENG',
        course_id='CS101',
        term='1'
    )
    
    db.session.add(program)
    db.session.add(course)
    db.session.add(requirement)
    db.session.commit()
    
    duplicate_data = {
        'program_id': 'SENG',
        'course_id': 'CS101',
        'term': '2'
    }
    
    response = client.post('/api/requirements/', json=duplicate_data)
    assert response.status_code == HTTPStatus.CONFLICT

def test_create_requirement_nonexistent_program(client):
    course = Course(
        course_id='CS101',
        course_name='Programming',
        credits=3.0
    )
    db.session.add(course)
    db.session.commit()
    
    requirement_data = {
        'program_id': 'NONEXISTENT',
        'course_id': 'CS101',
        'term': '1'
    }
    
    response = client.post('/api/requirements/', json=requirement_data)
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_create_requirement_nonexistent_course(client):
    program = Program(
        program_id='SENG',
        program_name='Software Engineering',
        total_enrollment=100,
        blocks_20_count=5,
        blocks_10_count=2
    )
    db.session.add(program)
    db.session.commit()
    
    requirement_data = {
        'program_id': 'SENG',
        'course_id': 'NONEXISTENT',
        'term': '1'
    }
    
    response = client.post('/api/requirements/', json=requirement_data)
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_get_nonexistent_program_requirements(client):
    response = client.get('/api/requirements/program/NONEXISTENT')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_create_requirement_missing_fields(client):
    incomplete_data = {
        'program_id': 'SENG',
        'course_id': 'CS101'
        # Missing term field
    }
    
    response = client.post('/api/requirements/', json=incomplete_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_get_program_requirements_empty(client):
    program = Program(
        program_id='SENG',
        program_name='Software Engineering',
        total_enrollment=100,
        blocks_20_count=5,
        blocks_10_count=2
    )
    db.session.add(program)
    db.session.commit()
    
    response = client.get('/api/requirements/program/SENG')
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.OK
    assert len(data) == 0

def test_create_requirement_invalid_term(client):
    program = Program(
        program_id='SENG',
        program_name='Software Engineering',
        total_enrollment=100,
        blocks_20_count=5,
        blocks_10_count=2
    )
    course = Course(
        course_id='CS101',
        course_name='Programming',
        credits=3.0
    )
    
    db.session.add(program)
    db.session.add(course)
    db.session.commit()
    
    requirement_data = {
        'program_id': 'SENG',
        'course_id': 'CS101',
        'term': '-1'  # Invalid term
    }
    
    response = client.post('/api/requirements/', json=requirement_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_create_requirement_no_data(client):
    response = client.post('/api/requirements/', json=None)
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

def test_multiple_requirements_same_program(client):
    program = Program(
        program_id='SENG',
        program_name='Software Engineering',
        total_enrollment=100,
        blocks_20_count=5,
        blocks_10_count=2
    )
    course1 = Course(
        course_id='CS101',
        course_name='Programming',
        credits=3.0
    )
    course2 = Course(
        course_id='CS102',
        course_name='Data Structures',
        credits=3.0
    )
    
    db.session.add(program)
    db.session.add(course1)
    db.session.add(course2)
    db.session.commit()
    
    requirement1 = {
        'program_id': 'SENG',
        'course_id': 'CS101',
        'term': '1'
    }
    requirement2 = {
        'program_id': 'SENG',
        'course_id': 'CS102',
        'term': '2'
    }
    
    response1 = client.post('/api/requirements/', json=requirement1)
    response2 = client.post('/api/requirements/', json=requirement2)
    
    assert response1.status_code == HTTPStatus.CREATED
    assert response2.status_code == HTTPStatus.CREATED
    
    response = client.get('/api/requirements/program/SENG')
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.OK
    assert len(data) == 2