# tests/test_programs.py
from http import HTTPStatus
from app import db
from app.models import Program

def test_get_programs(client):
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
    
    response = client.get('/api/programs/SENG')
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.OK
    assert data['program_id'] == 'SENG'
    assert data['program_name'] == 'Software Engineering'

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

def test_update_program(client):
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
        'total_enrollment': 150
    }
    
    response = client.put('/api/programs/SENG', json=update_data)
    data = response.get_json()
    
    assert response.status_code == HTTPStatus.OK
    assert data['program_name'] == update_data['program_name']
    assert data['total_enrollment'] == update_data['total_enrollment']

def test_delete_program(client):
    # Create test program
    program = Program(
        program_id='SENG',
        program_name='Software Engineering',
        total_enrollment=100,
        blocks_20_count=5,
        blocks_10_count=2
    )
    db.session.add(program)
    db.session.commit()
    
    # Delete program
    response = client.delete('/api/programs/SENG')
    assert response.status_code == HTTPStatus.NO_CONTENT
    
def test_create_program_invalid_data(client):
    invalid_data = {
        'program_id': 'SENG',
        'program_name': 'Software Engineering',
        'total_enrollment': -1,  # Invalid negative value
        'blocks_20_count': 5,
        'blocks_10_count': 2
    }
    
    response = client.post('/api/programs/', json=invalid_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
