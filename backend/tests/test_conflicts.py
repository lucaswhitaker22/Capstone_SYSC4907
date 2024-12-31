# tests/test_conflicts.py
from http import HTTPStatus
from datetime import time
from app import db
from app.models import CourseOffering, Course

def test_check_offering_conflict(client):
    # Create prerequisite course
    course = Course(course_id='CS101', course_name='Programming', credits=3.0)
    db.session.add(course)
    
    # Create two overlapping offerings
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
    
    db.session.add(offering1)
    db.session.add(offering2)
    db.session.commit()
    
    response = client.get('/api/conflicts/offerings/1/2')
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.OK
    assert data['has_conflict'] is True
    assert data['offering1'] == 'CS101'
    assert data['offering2'] == 'CS101'

def test_check_schedule_conflicts(client):
    # Create prerequisite course
    course = Course(course_id='CS101', course_name='Programming', credits=3.0)
    db.session.add(course)
    
    # Create three offerings, two with conflicts
    offerings = [
        CourseOffering(
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
        ),
        CourseOffering(
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
        ),
        CourseOffering(
            offering_id=3,
            course_id='CS101',
            section_type='LEC',
            section_code='C',
            day_of_week=2,  # Different day, no conflict
            start_time=time.fromisoformat('09:00'),
            end_time=time.fromisoformat('10:30'),
            capacity=50,
            term='1',
            academic_year='2024-25',
            status='ACTIVE',
            current_enrollment=0
        )
    ]
    
    for offering in offerings:
        db.session.add(offering)
    db.session.commit()
    
    response = client.post('/api/conflicts/schedule/conflicts', 
                          json={'offering_ids': [1, 2, 3]})
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.OK
    assert 'conflicts' in data
    assert len(data['conflicts']) == 1  # Only offerings 1 and 2 conflict
    assert data['conflicts'][0]['offering1_id'] == 1
    assert data['conflicts'][0]['offering2_id'] == 2

def test_check_course_conflicts(client):
    # Create prerequisite course
    course = Course(course_id='CS101', course_name='Programming', credits=3.0)
    db.session.add(course)
    
    # Create existing schedule offerings
    schedule_offering = CourseOffering(
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
    
    # Create new offering to check
    new_offering = CourseOffering(
        offering_id=2,
        course_id='CS101',
        section_type='LEC',
        section_code='B',
        day_of_week=1,
        start_time=time.fromisoformat('10:00'),  # Overlaps with schedule_offering
        end_time=time.fromisoformat('11:30'),
        capacity=50,
        term='1',
        academic_year='2024-25',
        status='ACTIVE',
        current_enrollment=0
    )
    
    db.session.add(schedule_offering)
    db.session.add(new_offering)
    db.session.commit()
    
    response = client.post('/api/conflicts/schedule/check-course',
                          json={
                              'schedule_offering_ids': [1],
                              'new_offering_id': 2
                          })
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.OK
    assert 'conflicts' in data
    assert len(data['conflicts']) == 1
    assert data['conflicts'][0]['existing_offering_id'] == 1
    assert data['conflicts'][0]['new_offering_id'] == 2
