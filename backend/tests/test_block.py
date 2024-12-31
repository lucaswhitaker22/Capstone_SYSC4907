# tests/test_block.py
from http import HTTPStatus

def test_get_blocks(client):
    sample_block = {
        'block_id': 'BLK1',
        'program_id': 'SENG',
        'block_size': 20,
        'term': '1',
        'academic_year': '2024-25',
        'schedule_rating': None,
        'status': 'DRAFT'
    }

    response = client.post('/api/blocks/', json=sample_block)
    assert response.status_code == HTTPStatus.CREATED

    response = client.get('/api/blocks/')
    data = response.get_json()

    assert response.status_code == HTTPStatus.OK
    assert len(data) == 1
    assert data[0]['block_id'] == sample_block['block_id']
    assert data[0]['program_id'] == sample_block['program_id']
    assert data[0]['block_size'] == sample_block['block_size']
    assert data[0]['term'] == sample_block['term']
    assert data[0]['academic_year'] == sample_block['academic_year']

def test_get_single_block(client):
    sample_block = {
        'block_id': 'BLK1',
        'program_id': 'SENG',
        'block_size': 20,
        'term': '1',
        'academic_year': '2024-25',
        'schedule_rating': None,
        'status': 'DRAFT'
    }

    response = client.post('/api/blocks/', json=sample_block)
    assert response.status_code == HTTPStatus.CREATED

    response = client.get(f"/api/blocks/{sample_block['block_id']}")
    data = response.get_json()

    assert response.status_code == HTTPStatus.OK
    assert data['block_id'] == sample_block['block_id']
    assert data['program_id'] == sample_block['program_id']
    assert data['block_size'] == sample_block['block_size']
    assert data['status'] == 'DRAFT'

def test_create_block(client):
    sample_block = {
        'block_id': 'BLK1',
        'program_id': 'SENG',
        'block_size': 20,
        'term': '1',
        'academic_year': '2024-25',
        'schedule_rating': None,
        'status': 'DRAFT'
    }

    response = client.post('/api/blocks/', json=sample_block)
    data = response.get_json()

    assert response.status_code == HTTPStatus.CREATED
    assert data['block_id'] == sample_block['block_id']
    assert data['program_id'] == sample_block['program_id']
    assert data['block_size'] == sample_block['block_size']

def test_create_block_missing_fields(client):
    incomplete_block = {
        'block_id': 'BLK1',
        'program_id': 'SENG'
    }

    response = client.post('/api/blocks/', json=incomplete_block)
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_create_duplicate_block(client):
    sample_block = {
        'block_id': 'BLK1',
        'program_id': 'SENG',
        'block_size': 20,
        'term': '1',
        'academic_year': '2024-25',
        'schedule_rating': None,
        'status': 'DRAFT'
    }

    response = client.post('/api/blocks/', json=sample_block)
    assert response.status_code == HTTPStatus.CREATED

    response = client.post('/api/blocks/', json=sample_block)
    assert response.status_code == HTTPStatus.CONFLICT

def test_update_block(client):
    sample_block = {
        'block_id': 'BLK1',
        'program_id': 'SENG',
        'block_size': 20,
        'term': '1',
        'academic_year': '2024-25',
        'schedule_rating': None,
        'status': 'DRAFT'
    }

    response = client.post('/api/blocks/', json=sample_block)
    assert response.status_code == HTTPStatus.CREATED

    update_data = {
        'block_size': 10,
        'status': 'PUBLISHED'
    }

    response = client.put(f"/api/blocks/{sample_block['block_id']}", json=update_data)
    data = response.get_json()

    assert response.status_code == HTTPStatus.OK
    assert data['block_size'] == update_data['block_size']
    assert data['status'] == update_data['status']

def test_delete_block(client):
    sample_block = {
        'block_id': 'BLK1',
        'program_id': 'SENG',
        'block_size': 20,
        'term': '1',
        'academic_year': '2024-25',
        'schedule_rating': None,
        'status': 'DRAFT'
    }

    response = client.post('/api/blocks/', json=sample_block)
    assert response.status_code == HTTPStatus.CREATED

    response = client.delete(f"/api/blocks/{sample_block['block_id']}")
    assert response.status_code == HTTPStatus.NO_CONTENT

    response = client.get(f"/api/blocks/{sample_block['block_id']}")
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_invalid_block_size(client):
    invalid_block = {
        'block_id': 'BLK1',
        'program_id': 'SENG',
        'block_size': 15,
        'term': '1',
        'academic_year': '2024-25',
        'schedule_rating': None,
        'status': 'DRAFT'
    }

    response = client.post('/api/blocks/', json=invalid_block)
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_get_nonexistent_block(client):
    response = client.get('/api/blocks/NOTFOUND')
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_update_block_status(client):
    sample_block = {
        'block_id': 'BLK1',
        'program_id': 'SENG',
        'block_size': 20,
        'term': '1',
        'academic_year': '2024-25',
        'status': 'DRAFT'
    }

    response = client.post('/api/blocks/', json=sample_block)
    assert response.status_code == HTTPStatus.CREATED

    # Test status update
    status_update = {'status': 'PUBLISHED'}
    response = client.patch(f"/api/blocks/{sample_block['block_id']}/status", 
                          json=status_update)
    data = response.get_json()

    assert response.status_code == HTTPStatus.OK
    assert data['status'] == 'PUBLISHED'

def test_invalid_status_update(client):
    sample_block = {
        'block_id': 'BLK1',
        'program_id': 'SENG',
        'block_size': 20,
        'term': '1',
        'academic_year': '2024-25',
        'status': 'DRAFT'
    }

    response = client.post('/api/blocks/', json=sample_block)
    assert response.status_code == HTTPStatus.CREATED

    # Test invalid status
    invalid_status = {'status': 'INVALID'}
    response = client.patch(f"/api/blocks/{sample_block['block_id']}/status", 
                          json=invalid_status)
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_delete_locked_block(client):
    sample_block = {
        'block_id': 'BLK1',
        'program_id': 'SENG',
        'block_size': 20,
        'term': '1',
        'academic_year': '2024-25',
        'status': 'DRAFT'
    }

    # Create and lock block
    response = client.post('/api/blocks/', json=sample_block)
    assert response.status_code == HTTPStatus.CREATED
    
    response = client.patch(f"/api/blocks/{sample_block['block_id']}/status", 
                          json={'status': 'LOCKED'})
    assert response.status_code == HTTPStatus.OK

    # Try to delete locked block
    response = client.delete(f"/api/blocks/{sample_block['block_id']}")
    assert response.status_code == HTTPStatus.FORBIDDEN

def test_calculate_block_rating(client):
    sample_block = {
        'block_id': 'BLK1',
        'program_id': 'SENG',
        'block_size': 20,
        'term': '1',
        'academic_year': '2024-25',
        'status': 'DRAFT'
    }

    response = client.post('/api/blocks/', json=sample_block)
    assert response.status_code == HTTPStatus.CREATED

    # Calculate ratings
    response = client.post(f"/api/blocks/{sample_block['block_id']}/rating")
    data = response.get_json()

    assert response.status_code == HTTPStatus.OK
    assert 'schedule_rating' in data
    assert 'early_starts' in data
    assert 'late_ends' in data
    assert 'long_breaks' in data
    assert 'consecutive_days' in data