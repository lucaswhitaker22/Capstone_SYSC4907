# app/routes/programs.py
from flask import Blueprint, jsonify, request
from app.models import Program, Block
from app import db
from http import HTTPStatus

bp = Blueprint('programs', __name__, url_prefix='/api/programs')

@bp.route('/', methods=['GET'], strict_slashes=False)
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

@bp.route('/<program_id>', methods=['GET'], strict_slashes=False)
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

        # Create program
        program = Program(**data)
        db.session.add(program)
        
        # Generate blocks
        blocks = []
        
        # Generate 20-student blocks
        for i in range(data['blocks_20_count']):
            block = Block(
                block_id=f"{data['program_id']}_20_{i+1}",
                program_id=data['program_id'],
                block_size=20,
                term="FALL",
                academic_year="2025-2026",
                status="ACTIVE"
            )
            blocks.append(block)
            
        # Generate 10-student blocks
        for i in range(data['blocks_10_count']):
            block = Block(
                block_id=f"{data['program_id']}_10_{i+1}",
                program_id=data['program_id'],
                block_size=10,
                term="FALL",
                academic_year="2025-2026",
                status="ACTIVE"
            )
            blocks.append(block)
        
        # Bulk save blocks
        db.session.bulk_save_objects(blocks)
        db.session.commit()
        
        return jsonify({
            'program_id': program.program_id,
            'program_name': program.program_name,
            'total_enrollment': program.total_enrollment,
            'blocks_20_count': program.blocks_20_count,
            'blocks_10_count': program.blocks_10_count,
            'blocks_created': len(blocks)
        }), HTTPStatus.CREATED
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR


@bp.route('/bulk', methods=['POST'])
def bulk_create_programs():
    try:
        data = request.get_json()
        if not data or 'programs' not in data:
            return jsonify({'error': 'No programs data provided'}), HTTPStatus.BAD_REQUEST
            
        programs = []
        blocks = []
        
        for program_data in data['programs']:
            if Program.query.get(program_data['program_id']):
                continue
                
            program = Program(
                program_id=program_data['program_id'],
                program_name=program_data['program_name'],
                total_enrollment=int(program_data['total_enrollment']),
                blocks_20_count=int(program_data['blocks_20_count']),
                blocks_10_count=int(program_data['blocks_10_count'])
            )
            programs.append(program)
            
            # Generate blocks for each program
            for i in range(int(program_data['blocks_20_count'])):
                blocks.append(Block(
                    block_id=f"{program_data['program_id']}_20_{i+1}",
                    program_id=program_data['program_id'],
                    block_size=20,
                    term="FALL",
                    academic_year="2025-2026",
                    status="ACTIVE"
                ))
                
            for i in range(int(program_data['blocks_10_count'])):
                blocks.append(Block(
                    block_id=f"{program_data['program_id']}_10_{i+1}",
                    program_id=program_data['program_id'],
                    block_size=10,
                    term="FALL",
                    academic_year="2025-2026",
                    status="ACTIVE"
                ))
        
        db.session.bulk_save_objects(programs)
        db.session.bulk_save_objects(blocks)
        db.session.commit()
        
        return jsonify({
            'message': f'{len(programs)} programs created with {len(blocks)} blocks'
        }), HTTPStatus.CREATED
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST
    
@bp.route('/<program_id>', methods=['PUT'], strict_slashes=False)
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

@bp.route('/<program_id>', methods=['DELETE'], strict_slashes=False)
def delete_program(program_id):
    program = Program.query.get_or_404(program_id)
    db.session.delete(program)
    db.session.commit()
    return '', HTTPStatus.NO_CONTENT

@bp.route('/<program_id>/enrollment', methods=['PATCH'], strict_slashes=False)
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

@bp.route('/<program_id>/blocks', methods=['PATCH'], strict_slashes=False)
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