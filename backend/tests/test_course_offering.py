# tests/test_course_offerings.py
from http import HTTPStatus
from datetime import time
from app import db
from app.models import Course, CourseOffering

def test_get_offerings(client):
    # Create prerequisite course
    course = Course(course_id='CS101', course_name='Programming', credits=3.0)
    db.session.add(course)
    
    # Create test offering
    offering = CourseOffering(
        course_id='CS101',
        section_type='LEC',
        section_code='A',
        day_of_week=1,
        start_time=time.fromisoformat('08:30'),
        end_time=time.fromisoformat('10:00'),
        capacity=50,
        current_enrollment=0,
        term='1',
        academic_year='2024-25',
        status='ACTIVE'
    )
    db.session.add(offering)
    db.session.commit()
    
    response = client.get('/api/offerings/')
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.OK
    assert len(data) == 1
    assert data[0]['course_id'] == 'CS101'
    assert data[0]['section_type'] == 'LEC'
    assert data[0]['start_time'] == '08:30'
    assert data[0]['capacity'] == 50

def test_get_single_offering(client):
    # Create prerequisite course
    course = Course(course_id='CS101', course_name='Programming', credits=3.0)
    offering = CourseOffering(
        course_id='CS101',
        section_type='LEC',
        section_code='A',
        day_of_week=1,
        start_time=time.fromisoformat('08:30'),
        end_time=time.fromisoformat('10:00'),
        capacity=50,
        current_enrollment=0,
        term='1',
        academic_year='2024-25',
        status='ACTIVE'
    )
    db.session.add(course)
    db.session.add(offering)
    db.session.commit()
    
    response = client.get(f'/api/offerings/{offering.offering_id}')
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.OK
    assert data['course_id'] == 'CS101'
    assert data['section_type'] == 'LEC'
    assert data['start_time'] == '08:30'

def test_create_offering(client):
    # Create prerequisite course
    course = Course(course_id='CS101', course_name='Programming', credits=3.0)
    db.session.add(course)
    db.session.commit()
    
    offering_data = {
        'course_id': 'CS101',
        'section_type': 'LEC',
        'section_code': 'A',
        'day_of_week': 1,
        'start_time': '08:30',
        'end_time': '10:00',
        'capacity': 50,
        'term': '1',
        'academic_year': '2024-25'
    }
    
    response = client.post('/api/offerings/', json=offering_data)
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.CREATED
    assert data['course_id'] == offering_data['course_id']
    assert data['section_type'] == offering_data['section_type']
    assert data['start_time'] == offering_data['start_time']

def test_create_offering_missing_fields(client):
    incomplete_data = {
        'course_id': 'CS101',
        'section_type': 'LEC'
    }
    
    response = client.post('/api/offerings/', json=incomplete_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_create_offering_nonexistent_course(client):
    offering_data = {
        'course_id': 'NOTFOUND',
        'section_type': 'LEC',
        'section_code': 'A',
        'day_of_week': 1,
        'start_time': '08:30',
        'end_time': '10:00',
        'capacity': 50,
        'term': '1',
        'academic_year': '2024-25'
    }
    
    response = client.post('/api/offerings/', json=offering_data)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_offering(client):
    # Create prerequisite course and offering
    course = Course(course_id='CS101', course_name='Programming', credits=3.0)
    offering = CourseOffering(
        course_id='CS101',
        section_type='LEC',
        section_code='A',
        day_of_week=1,
        start_time=time.fromisoformat('08:30'),
        end_time=time.fromisoformat('10:00'),
        capacity=50,
        current_enrollment=0,
        term='1',
        academic_year='2024-25',
        status='ACTIVE'
    )
    db.session.add(course)
    db.session.add(offering)
    db.session.commit()
    
    response = client.delete(f'/api/offerings/{offering.offering_id}')
    assert response.status_code == HTTPStatus.NO_CONTENT
    
    # Verify deletion
    response = client.get(f'/api/offerings/{offering.offering_id}')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_invalid_time_format(client):
    course = Course(course_id='CS101', course_name='Programming', credits=3.0)
    db.session.add(course)
    db.session.commit()
    
    offering_data = {
        'course_id': 'CS101',
        'section_type': 'LEC',
        'section_code': 'A',
        'day_of_week': 1,
        'start_time': '8:30AM',  # Invalid format
        'end_time': '10:00',
        'capacity': 50,
        'term': '1',
        'academic_year': '2024-25'
    }
    
    response = client.post('/api/offerings/', json=offering_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_update_enrollment(client):
    # Create prerequisite course and offering
    course = Course(course_id='CS101', course_name='Programming', credits=3.0)
    offering = CourseOffering(
        course_id='CS101',
        section_type='LEC',
        section_code='A',
        day_of_week=1,
        start_time=time.fromisoformat('08:30'),
        end_time=time.fromisoformat('10:00'),
        capacity=50,
        current_enrollment=0,
        term='1',
        academic_year='2024-25',
        status='OPEN'
    )
    db.session.add(course)
    db.session.add(offering)
    db.session.commit()
    
    # Update enrollment to full capacity
    response = client.patch(f'/api/offerings/{offering.offering_id}/enrollment', 
                          json={'current_enrollment': 50})
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.OK
    assert data['current_enrollment'] == 50
    assert data['status'] == 'FULL'

def test_invalid_enrollment_update(client):
    # Create prerequisite course and offering
    course = Course(course_id='CS101', course_name='Programming', credits=3.0)
    offering = CourseOffering(
        course_id='CS101',
        section_type='LEC',
        section_code='A',
        day_of_week=1,
        start_time=time.fromisoformat('08:30'),
        end_time=time.fromisoformat('10:00'),
        capacity=50,
        current_enrollment=0,
        term='1',
        academic_year='2024-25',
        status='OPEN'
    )
    db.session.add(course)
    db.session.add(offering)
    db.session.commit()
    
    # Try negative enrollment
    response = client.patch(f'/api/offerings/{offering.offering_id}/enrollment', 
                          json={'current_enrollment': -1})
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_update_offering_status(client):
    # Create prerequisite course and offering
    course = Course(course_id='CS101', course_name='Programming', credits=3.0)
    offering = CourseOffering(
        course_id='CS101',
        section_type='LEC',
        section_code='A',
        day_of_week=1,
        start_time=time.fromisoformat('08:30'),
        end_time=time.fromisoformat('10:00'),
        capacity=50,
        current_enrollment=0,
        term='1',
        academic_year='2024-25',
        status='OPEN'
    )
    db.session.add(course)
    db.session.add(offering)
    db.session.commit()
    
    # Update status to CANCELLED
    response = client.patch(f'/api/offerings/{offering.offering_id}/status', 
                          json={'status': 'CANCELLED'})
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.OK
    assert data['status'] == 'CANCELLED'

def test_invalid_status_update(client):
    # Create prerequisite course and offering
    course = Course(course_id='CS101', course_name='Programming', credits=3.0)
    offering = CourseOffering(
        course_id='CS101',
        section_type='LEC',
        section_code='A',
        day_of_week=1,
        start_time=time.fromisoformat('08:30'),
        end_time=time.fromisoformat('10:00'),
        capacity=50,
        current_enrollment=0,
        term='1',
        academic_year='2024-25',
        status='OPEN'
    )
    db.session.add(course)
    db.session.add(offering)
    db.session.commit()
    
    # Try invalid status
    response = client.patch(f'/api/offerings/{offering.offering_id}/status', 
                          json={'status': 'INVALID'})
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_delete_offering_with_enrollment(client):
    # Create prerequisite course and offering
    course = Course(course_id='CS101', course_name='Programming', credits=3.0)
    offering = CourseOffering(
        course_id='CS101',
        section_type='LEC',
        section_code='A',
        day_of_week=1,
        start_time=time.fromisoformat('08:30'),
        end_time=time.fromisoformat('10:00'),
        capacity=50,
        current_enrollment=10,
        term='1',
        academic_year='2024-25',
        status='OPEN'
    )
    db.session.add(course)
    db.session.add(offering)
    db.session.commit()
    
    # Try to delete offering with enrollment
    response = client.delete(f'/api/offerings/{offering.offering_id}')
    assert response.status_code == HTTPStatus.CONFLICT
