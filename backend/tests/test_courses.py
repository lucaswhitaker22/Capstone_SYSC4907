# tests/test_courses.py
import pytest
from app.models import Course
from http import HTTPStatus

def test_get_courses_empty(client):
    response = client.get('/api/courses/')
    assert response.status_code == HTTPStatus.OK
    assert response.json == []

def test_get_courses(client, sample_course):
    # Create test course
    client.post('/api/courses/', json=sample_course)
    
    response = client.get('/api/courses/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.json) == 1
    assert response.json[0]['course_id'] == sample_course['course_id']
    assert response.json[0]['course_name'] == sample_course['course_name']
    assert response.json[0]['credits'] == sample_course['credits']

def test_get_course(client, sample_course):
    # Create test course
    client.post('/api/courses/', json=sample_course)
    
    response = client.get(f"/api/courses/{sample_course['course_id']}")
    assert response.status_code == HTTPStatus.OK
    assert response.json['course_id'] == sample_course['course_id']
    assert response.json['course_name'] == sample_course['course_name']
    assert response.json['credits'] == sample_course['credits']

def test_get_course_not_found(client):
    response = client.get('/api/courses/NOTFOUND')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_create_course(client, sample_course):
    response = client.post('/api/courses/', json=sample_course)
    assert response.status_code == HTTPStatus.CREATED
    assert response.json['course_id'] == sample_course['course_id']
    assert response.json['course_name'] == sample_course['course_name']
    assert response.json['credits'] == sample_course['credits']

def test_create_duplicate_course(client, sample_course):
    # Create first course
    client.post('/api/courses/', json=sample_course)
    
    # Try to create duplicate
    response = client.post('/api/courses/', json=sample_course)
    assert response.status_code == HTTPStatus.CONFLICT

def test_create_course_invalid_data(client):
    # Test missing fields
    invalid_course = {
        'course_id': 'CS101'
        # Missing course_name and credits
    }
    response = client.post('/api/courses/', json=invalid_course)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'error' in response.json
    assert response.json['error'] == 'Missing required fields'
    
    # Test empty request
    response = client.post('/api/courses/', json={})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'error' in response.json


def test_update_course(client, sample_course):
    # Create test course
    client.post('/api/courses/', json=sample_course)
    
    # Update course
    updated_data = {
        'course_name': 'Updated Course Name',
        'credits': 4.0
    }
    response = client.put(f"/api/courses/{sample_course['course_id']}", json=updated_data)
    assert response.status_code == HTTPStatus.OK
    assert response.json['course_name'] == updated_data['course_name']
    assert response.json['credits'] == updated_data['credits']

def test_update_course_not_found(client):
    response = client.put('/api/courses/NOTFOUND', json={'course_name': 'Test'})
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_delete_course(client, sample_course):
    # Create test course
    client.post('/api/courses/', json=sample_course)
    
    # Delete course
    response = client.delete(f"/api/courses/{sample_course['course_id']}")
    assert response.status_code == HTTPStatus.NO_CONTENT
    
    # Verify deletion
    get_response = client.get(f"/api/courses/{sample_course['course_id']}")
    assert get_response.status_code == HTTPStatus.NOT_FOUND

def test_delete_course_not_found(client):
    response = client.delete('/api/courses/NOTFOUND')
    assert response.status_code == HTTPStatus.NOT_FOUND
