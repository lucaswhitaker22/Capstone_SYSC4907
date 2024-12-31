# tests/test_schedules.py
from http import HTTPStatus
from datetime import time
from app import db
from app.models import CourseOffering, Block, Course

def test_add_offering_to_block(client):
    # Create prerequisite course
    course = Course(course_id='CS101', course_name='Programming', credits=3.0)
    db.session.add(course)
    
    # Create block
    block = Block(
        block_id='BLK1',
        program_id='SENG',
        block_size=20,
        term='1',
        academic_year='2024-25',
        status='DRAFT'
    )
    
    # Create offering with all required fields
    offering = CourseOffering(
        offering_id=1,
        course_id='CS101',
        section_type='LEC',
        section_code='A',
        day_of_week=1,
        start_time=time.fromisoformat('08:30'),
        end_time=time.fromisoformat('10:00'),
        capacity=50,
        term='1',
        academic_year='2024-25',
        status='ACTIVE',
        current_enrollment=0
    )
    
    db.session.add(block)
    db.session.add(offering)
    db.session.commit()
    
    response = client.post('/api/schedules/block/BLK1', json={'offering_id': 1})
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.CREATED
    assert data['block_id'] == 'BLK1'
    assert data['offering_id'] == 1
    assert data['course_id'] == 'CS101'
    assert data['start_time'] == '08:30'
    assert data['end_time'] == '10:00'

def test_missing_offering_id(client):
    block = Block(
        block_id='BLK1',
        program_id='SENG',
        block_size=20,
        term='1',
        academic_year='2024-25',
        status='DRAFT'
    )
    db.session.add(block)
    db.session.commit()
    
    response = client.post('/api/schedules/block/BLK1', json={})
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_nonexistent_block(client):
    course = Course(course_id='CS101', course_name='Programming', credits=3.0)
    offering = CourseOffering(
        offering_id=1,
        course_id='CS101',
        section_type='LEC',
        section_code='A',
        day_of_week=1,
        start_time=time.fromisoformat('08:30'),
        end_time=time.fromisoformat('10:00'),
        capacity=50,
        term='1',
        academic_year='2024-25',
        status='ACTIVE',
        current_enrollment=0
    )
    db.session.add(course)
    db.session.add(offering)
    db.session.commit()
    
    response = client.post('/api/schedules/block/NONEXISTENT', json={'offering_id': 1})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_duplicate_offering(client):
    # Setup prerequisites
    course = Course(course_id='CS101', course_name='Programming', credits=3.0)
    block = Block(
        block_id='BLK1',
        program_id='SENG',
        block_size=20,
        term='1',
        academic_year='2024-25',
        status='DRAFT'
    )
    offering = CourseOffering(
        offering_id=1,
        course_id='CS101',
        section_type='LEC',
        section_code='A',
        day_of_week=1,
        start_time=time.fromisoformat('08:30'),
        end_time=time.fromisoformat('10:00'),
        capacity=50,
        term='1',
        academic_year='2024-25',
        status='ACTIVE',
        current_enrollment=0
    )
    
    db.session.add(course)
    db.session.add(block)
    db.session.add(offering)
    db.session.commit()
    
    # First addition
    response = client.post('/api/schedules/block/BLK1', json={'offering_id': 1})
    assert response.status_code == HTTPStatus.CREATED
    
    # Duplicate addition
    response = client.post('/api/schedules/block/BLK1', json={'offering_id': 1})
    assert response.status_code == HTTPStatus.CONFLICT

def test_time_conflict(client):
    # Setup prerequisites
    course = Course(course_id='CS101', course_name='Programming', credits=3.0)
    block = Block(
        block_id='BLK1',
        program_id='SENG',
        block_size=20,
        term='1',
        academic_year='2024-25',
        status='DRAFT'
    )
    
    offering1 = CourseOffering(
        offering_id=1,
        course_id='CS101',
        section_type='LEC',
        section_code='A',
        day_of_week=1,
        start_time=time.fromisoformat('09:00'),
        end_time=time.fromisoformat('10:30'),
        capacity=50,
        term='1',
        academic_year='2024-25',
        status='ACTIVE',
        current_enrollment=0
    )
    
    offering2 = CourseOffering(
        offering_id=2,
        course_id='CS101',
        section_type='LEC',
        section_code='B',
        day_of_week=1,
        start_time=time.fromisoformat('10:00'),
        end_time=time.fromisoformat('11:30'),
        capacity=50,
        term='1',
        academic_year='2024-25',
        status='ACTIVE',
        current_enrollment=0
    )
    
    db.session.add(course)
    db.session.add(block)
    db.session.add(offering1)
    db.session.add(offering2)
    db.session.commit()
    
    # Add first offering
    response = client.post('/api/schedules/block/BLK1', json={'offering_id': 1})
    assert response.status_code == HTTPStatus.CREATED
    
    # Try to add conflicting offering
    response = client.post('/api/schedules/block/BLK1', json={'offering_id': 2})
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.CONFLICT
    assert 'conflicts' in data
    assert len(data['conflicts']) == 1
    assert data['conflicts'][0]['existing_offering_id'] == 1
    assert data['conflicts'][0]['new_offering_id'] == 2
