# app/routes/programs.py
from flask import Blueprint, jsonify, request
from app.models import Program
from app import db
from http import HTTPStatus

bp = Blueprint('programs', __name__, url_prefix='/api/programs')

@bp.route('/', methods=['GET'])
def get_programs():
    try:
        programs = Program.query.all()
        return jsonify([{
            'program_id': p.program_id,
            'program_name': p.program_name,
            'total_enrollment': p.total_enrollment,
            'blocks_20_count': p.blocks_20_count,
            'blocks_10_count': p.blocks_10_count
        } for p in programs]), HTTPStatus.OK
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<program_id>', methods=['GET'])
def get_program(program_id):
    program = Program.query.get_or_404(program_id)
    return jsonify({
        'program_id': program.program_id,
        'program_name': program.program_name,
        'total_enrollment': program.total_enrollment,
        'blocks_20_count': program.blocks_20_count,
        'blocks_10_count': program.blocks_10_count
    }), HTTPStatus.OK

@bp.route('/', methods=['POST'])
def create_program():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['program_id', 'program_name', 'total_enrollment', 
                         'blocks_20_count', 'blocks_10_count']
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), HTTPStatus.BAD_REQUEST
        
        # Check for existing program
        if Program.query.get(data['program_id']):
            return jsonify({'error': 'Program already exists'}), HTTPStatus.CONFLICT
            
        # Validate numeric fields
        if not isinstance(data['total_enrollment'], int) or data['total_enrollment'] < 0:
            return jsonify({'error': 'Invalid total_enrollment'}), HTTPStatus.BAD_REQUEST
            
        if not isinstance(data['blocks_20_count'], int) or data['blocks_20_count'] < 0:
            return jsonify({'error': 'Invalid blocks_20_count'}), HTTPStatus.BAD_REQUEST
            
        if not isinstance(data['blocks_10_count'], int) or data['blocks_10_count'] < 0:
            return jsonify({'error': 'Invalid blocks_10_count'}), HTTPStatus.BAD_REQUEST

        program = Program(**data)
        db.session.add(program)
        db.session.commit()
        
        return jsonify({
            'program_id': program.program_id,
            'program_name': program.program_name,
            'total_enrollment': program.total_enrollment,
            'blocks_20_count': program.blocks_20_count,
            'blocks_10_count': program.blocks_10_count
        }), HTTPStatus.CREATED
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<program_id>', methods=['PUT'])
def update_program(program_id):
    program = Program.query.get_or_404(program_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), HTTPStatus.BAD_REQUEST
        
    if 'program_name' in data:
        program.program_name = data['program_name']
    if 'total_enrollment' in data:
        if not isinstance(data['total_enrollment'], int) or data['total_enrollment'] < 0:
            return jsonify({'error': 'Invalid total_enrollment'}), HTTPStatus.BAD_REQUEST
        program.total_enrollment = data['total_enrollment']
    if 'blocks_20_count' in data:
        if not isinstance(data['blocks_20_count'], int) or data['blocks_20_count'] < 0:
            return jsonify({'error': 'Invalid blocks_20_count'}), HTTPStatus.BAD_REQUEST
        program.blocks_20_count = data['blocks_20_count']
    if 'blocks_10_count' in data:
        if not isinstance(data['blocks_10_count'], int) or data['blocks_10_count'] < 0:
            return jsonify({'error': 'Invalid blocks_10_count'}), HTTPStatus.BAD_REQUEST
        program.blocks_10_count = data['blocks_10_count']
        
    db.session.commit()
    
    return jsonify({
        'program_id': program.program_id,
        'program_name': program.program_name,
        'total_enrollment': program.total_enrollment,
        'blocks_20_count': program.blocks_20_count,
        'blocks_10_count': program.blocks_10_count
    }), HTTPStatus.OK

@bp.route('/<program_id>', methods=['DELETE'])
def delete_program(program_id):
    program = Program.query.get_or_404(program_id)
    db.session.delete(program)
    db.session.commit()
    return '', HTTPStatus.NO_CONTENT

@bp.route('/<program_id>/enrollment', methods=['PATCH'])
def update_enrollment(program_id):
    try:
        program = Program.query.get_or_404(program_id)
        data = request.get_json()
        
        if 'total_enrollment' not in data:
            return jsonify({'error': 'Missing total_enrollment'}), HTTPStatus.BAD_REQUEST
            
        if not isinstance(data['total_enrollment'], int) or data['total_enrollment'] < 0:
            return jsonify({'error': 'Invalid total_enrollment'}), HTTPStatus.BAD_REQUEST
            
        program.total_enrollment = data['total_enrollment']
        db.session.commit()
        
        return jsonify({
            'program_id': program.program_id,
            'total_enrollment': program.total_enrollment
        }), HTTPStatus.OK
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<program_id>/blocks', methods=['PATCH'])
def update_block_counts(program_id):
    try:
        program = Program.query.get_or_404(program_id)
        data = request.get_json()
        
        if 'blocks_20_count' in data:
            if not isinstance(data['blocks_20_count'], int) or data['blocks_20_count'] < 0:
                return jsonify({'error': 'Invalid blocks_20_count'}), HTTPStatus.BAD_REQUEST
            program.blocks_20_count = data['blocks_20_count']
            
        if 'blocks_10_count' in data:
            if not isinstance(data['blocks_10_count'], int) or data['blocks_10_count'] < 0:
                return jsonify({'error': 'Invalid blocks_10_count'}), HTTPStatus.BAD_REQUEST
            program.blocks_10_count = data['blocks_10_count']
            
        db.session.commit()
        
        return jsonify({
            'program_id': program.program_id,
            'blocks_20_count': program.blocks_20_count,
            'blocks_10_count': program.blocks_10_count
        }), HTTPStatus.OK
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR