# tests/test_course.py
from http import HTTPStatus

def test_get_courses(client):
    sample_course = {
        'course_id': 'CS101',
        'course_name': 'Introduction to Programming',
        'credits': 3.0
    }

    response = client.post('/api/courses/', json=sample_course)
    assert response.status_code == HTTPStatus.CREATED

    response = client.get('/api/courses/')
    data = response.get_json()

    assert response.status_code == HTTPStatus.OK
    assert len(data) == 1
    assert data[0]['course_id'] == sample_course['course_id']
    assert data[0]['course_name'] == sample_course['course_name']
    assert data[0]['credits'] == sample_course['credits']

def test_get_single_course(client):
    sample_course = {
        'course_id': 'CS101',
        'course_name': 'Introduction to Programming',
        'credits': 3.0
    }

    response = client.post('/api/courses/', json=sample_course)
    assert response.status_code == HTTPStatus.CREATED

    response = client.get(f"/api/courses/{sample_course['course_id']}")
    data = response.get_json()

    assert response.status_code == HTTPStatus.OK
    assert data['course_id'] == sample_course['course_id']
    assert data['course_name'] == sample_course['course_name']
    assert data['credits'] == sample_course['credits']

def test_create_course(client):
    sample_course = {
        'course_id': 'CS101',
        'course_name': 'Introduction to Programming',
        'credits': 3.0
    }

    response = client.post('/api/courses/', json=sample_course)
    data = response.get_json()

    assert response.status_code == HTTPStatus.CREATED
    assert data['course_id'] == sample_course['course_id']
    assert data['course_name'] == sample_course['course_name']
    assert data['credits'] == sample_course['credits']

def test_create_duplicate_course(client):
    sample_course = {
        'course_id': 'CS101',
        'course_name': 'Introduction to Programming',
        'credits': 3.0
    }

    response = client.post('/api/courses/', json=sample_course)
    assert response.status_code == HTTPStatus.CREATED

    response = client.post('/api/courses/', json=sample_course)
    assert response.status_code == HTTPStatus.CONFLICT

def test_update_course(client):
    sample_course = {
        'course_id': 'CS101',
        'course_name': 'Introduction to Programming',
        'credits': 3.0
    }

    response = client.post('/api/courses/', json=sample_course)
    assert response.status_code == HTTPStatus.CREATED

    update_data = {
        'course_name': 'Advanced Programming',
        'credits': 4.0
    }

    response = client.put(f"/api/courses/{sample_course['course_id']}", json=update_data)
    data = response.get_json()

    assert response.status_code == HTTPStatus.OK
    assert data['course_name'] == update_data['course_name']
    assert data['credits'] == update_data['credits']

def test_delete_course(client):
    sample_course = {
        'course_id': 'CS101',
        'course_name': 'Introduction to Programming',
        'credits': 3.0
    }

    response = client.post('/api/courses/', json=sample_course)
    assert response.status_code == HTTPStatus.CREATED

    response = client.delete(f"/api/courses/{sample_course['course_id']}")
    assert response.status_code == HTTPStatus.NO_CONTENT

    response = client.get(f"/api/courses/{sample_course['course_id']}")
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_get_nonexistent_course(client):
    response = client.get('/api/courses/NOTFOUND')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_update_nonexistent_course(client):
    update_data = {
        'course_name': 'New Name',
        'credits': 3.0
    }
    response = client.put('/api/courses/NOTFOUND', json=update_data)
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_delete_nonexistent_course(client):
    response = client.delete('/api/courses/NOTFOUND')
    assert response.status_code == HTTPStatus.NOT_FOUND
