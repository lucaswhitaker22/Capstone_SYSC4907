# tests/test_programs.py
from http import HTTPStatus
from app import db
from app.models import Program

def test_get_programs(client):
    # Create sample program
    program = Program(
        program_id='SENG',
        program_name='Software Engineering',
        total_enrollment=100,
        blocks_20_count=5,
        blocks_10_count=2
    )
    db.session.add(program)
    db.session.commit()
    
    response = client.get('/api/programs/')
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.OK
    assert len(data) == 1
    assert data[0]['program_id'] == 'SENG'
    assert data[0]['program_name'] == 'Software Engineering'
    assert data[0]['total_enrollment'] == 100
    assert data[0]['blocks_20_count'] == 5
    assert data[0]['blocks_10_count'] == 2

def test_get_single_program(client):
    program = Program(
        program_id='SENG',
        program_name='Software Engineering',
        total_enrollment=100,
        blocks_20_count=5,
        blocks_10_count=2
    )
    db.session.add(program)
    db.session.commit()
    
    response = client.get(f"/api/programs/{program.program_id}")
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.OK
    assert data['program_id'] == 'SENG'
    assert data['program_name'] == 'Software Engineering'
    assert data['total_enrollment'] == 100
    assert data['blocks_20_count'] == 5
    assert data['blocks_10_count'] == 2

def test_create_program(client):
    program_data = {
        'program_id': 'SENG',
        'program_name': 'Software Engineering',
        'total_enrollment': 100,
        'blocks_20_count': 5,
        'blocks_10_count': 2
    }
    
    response = client.post('/api/programs/', json=program_data)
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.CREATED
    assert data['program_id'] == program_data['program_id']
    assert data['program_name'] == program_data['program_name']
    assert data['total_enrollment'] == program_data['total_enrollment']
    assert data['blocks_20_count'] == program_data['blocks_20_count']
    assert data['blocks_10_count'] == program_data['blocks_10_count']

def test_create_program_missing_fields(client):
    incomplete_data = {
        'program_id': 'SENG',
        'program_name': 'Software Engineering'
    }
    
    response = client.post('/api/programs/', json=incomplete_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_create_duplicate_program(client):
    program_data = {
        'program_id': 'SENG',
        'program_name': 'Software Engineering',
        'total_enrollment': 100,
        'blocks_20_count': 5,
        'blocks_10_count': 2
    }
    
    # Create first program
    response = client.post('/api/programs/', json=program_data)
    assert response.status_code == HTTPStatus.CREATED
    
    # Try to create duplicate
    response = client.post('/api/programs/', json=program_data)
    assert response.status_code == HTTPStatus.CONFLICT

def test_update_program(client):
    # Create initial program
    program = Program(
        program_id='SENG',
        program_name='Software Engineering',
        total_enrollment=100,
        blocks_20_count=5,
        blocks_10_count=2
    )
    db.session.add(program)
    db.session.commit()
    
    update_data = {
        'program_name': 'Updated Engineering',
        'total_enrollment': 150,
        'blocks_20_count': 6,
        'blocks_10_count': 3
    }
    
    response = client.put(f"/api/programs/{program.program_id}", json=update_data)
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.OK
    assert data['program_name'] == update_data['program_name']
    assert data['total_enrollment'] == update_data['total_enrollment']
    assert data['blocks_20_count'] == update_data['blocks_20_count']
    assert data['blocks_10_count'] == update_data['blocks_10_count']

def test_update_nonexistent_program(client):
    update_data = {
        'program_name': 'Updated Engineering'
    }
    
    response = client.put('/api/programs/NOTFOUND', json=update_data)
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_delete_program(client):
    program = Program(
        program_id='SENG',
        program_name='Software Engineering',
        total_enrollment=100,
        blocks_20_count=5,
        blocks_10_count=2
    )
    db.session.add(program)
    db.session.commit()
    
    response = client.delete(f"/api/programs/{program.program_id}")
    assert response.status_code == HTTPStatus.NO_CONTENT
    
    # Verify program is deleted
    response = client.get(f"/api/programs/{program.program_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND

def test_invalid_enrollment_values(client):
    invalid_data = {
        'program_id': 'SENG',
        'program_name': 'Software Engineering',
        'total_enrollment': -1,
        'blocks_20_count': 5,
        'blocks_10_count': 2
    }
    
    response = client.post('/api/programs/', json=invalid_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
