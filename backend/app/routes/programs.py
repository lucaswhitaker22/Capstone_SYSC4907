# app/routes/programs.py
from flask import Blueprint, jsonify, request
from app.models import Program, Block, ProgramRequirement, BlockSchedule
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
            'blocks_20_count_fall': p.blocks_20_count_fall,
            'blocks_10_count_fall': p.blocks_10_count_fall,
            'blocks_20_count_winter': p.blocks_20_count_winter,
            'blocks_10_count_winter': p.blocks_10_count_winter
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
        'blocks_20_count_fall': program.blocks_20_count_fall,
        'blocks_10_count_fall': program.blocks_10_count_fall,
        'blocks_20_count_winter': program.blocks_20_count_winter,
        'blocks_10_count_winter': program.blocks_10_count_winter
    }), HTTPStatus.OK


@bp.route('/', methods=['POST'])
def create_program():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'program_id', 'program_name', 'total_enrollment',
            'blocks_20_count_fall', 'blocks_10_count_fall',
            'blocks_20_count_winter', 'blocks_10_count_winter',
            'term', 'academic_year'
        ]
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), HTTPStatus.BAD_REQUEST
            
        # Validate term
        if data['term'] not in ['FALL', 'WINTER']:
            return jsonify({'error': 'Invalid term'}), HTTPStatus.BAD_REQUEST

        # Create program
        program = Program(
            program_id=data['program_id'],
            program_name=data['program_name'],
            total_enrollment=data['total_enrollment'],
            blocks_20_count_fall=data['blocks_20_count_fall'],
            blocks_10_count_fall=data['blocks_10_count_fall'],
            blocks_20_count_winter=data['blocks_20_count_winter'],
            blocks_10_count_winter=data['blocks_10_count_winter']
        )
        db.session.add(program)
        
        # Generate blocks for specified term
        blocks = []
        
        if data['term'] == 'FALL':
            block_counts = {
                20: data['blocks_20_count_fall'],
                10: data['blocks_10_count_fall']
            }
        else:  # WINTER
            block_counts = {
                20: data['blocks_20_count_winter'],
                10: data['blocks_10_count_winter']
            }

        # Generate blocks
        for size, count in block_counts.items():
            for i in range(count):
                block = Block(
                    block_id=f"{data['program_id']}_{data['term'][0]}_{size}_{i+1}",
                    program_id=data['program_id'],
                    block_size=size,
                    term=data['term'],
                    academic_year=data['academic_year'],
                    status="DRAFT"
                )
                blocks.append(block)
        
        db.session.bulk_save_objects(blocks)
        db.session.commit()
        
        return jsonify({
            'program_id': program.program_id,
            'program_name': program.program_name,
            'total_enrollment': program.total_enrollment,
            'blocks_20_count_fall': program.blocks_20_count_fall,
            'blocks_10_count_fall': program.blocks_10_count_fall,
            'blocks_20_count_winter': program.blocks_20_count_winter,
            'blocks_10_count_winter': program.blocks_10_count_winter,
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
                blocks_20_count_fall=int(program_data.get('blocks_20_count_fall', 0)),
                blocks_10_count_fall=int(program_data.get('blocks_10_count_fall', 0)),
                blocks_20_count_winter=int(program_data.get('blocks_20_count_winter', 0)),
                blocks_10_count_winter=int(program_data.get('blocks_10_count_winter', 0))
            )
            programs.append(program)
            
            # Generate Fall blocks
            for i in range(int(program_data.get('blocks_20_count_fall', 0))):
                blocks.append(Block(
                    block_id=f"{program_data['program_id']}_F_20_{i+1}",
                    program_id=program_data['program_id'],
                    block_size=20,
                    term="FALL",
                    academic_year="2025-2026",
                    status="DRAFT"
                ))
                
            for i in range(int(program_data.get('blocks_10_count_fall', 0))):
                blocks.append(Block(
                    block_id=f"{program_data['program_id']}_F_10_{i+1}",
                    program_id=program_data['program_id'],
                    block_size=10,
                    term="FALL",
                    academic_year="2025-2026",
                    status="DRAFT"
                ))
                
            # Generate Winter blocks
            for i in range(int(program_data.get('blocks_20_count_winter', 0))):
                blocks.append(Block(
                    block_id=f"{program_data['program_id']}_W_20_{i+1}",
                    program_id=program_data['program_id'],
                    block_size=20,
                    term="WINTER",
                    academic_year="2025-2026",
                    status="DRAFT"
                ))
                
            for i in range(int(program_data.get('blocks_10_count_winter', 0))):
                blocks.append(Block(
                    block_id=f"{program_data['program_id']}_W_10_{i+1}",
                    program_id=program_data['program_id'],
                    block_size=10,
                    term="WINTER",
                    academic_year="2025-2026",
                    status="DRAFT"
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
    try:
        program = Program.query.get_or_404(program_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), HTTPStatus.BAD_REQUEST

        # Update basic program fields
        if 'program_name' in data:
            program.program_name = data['program_name']
            
        if 'total_enrollment' in data:
            if not isinstance(data['total_enrollment'], int) or data['total_enrollment'] < 0:
                return jsonify({'error': 'Invalid total_enrollment'}), HTTPStatus.BAD_REQUEST
            program.total_enrollment = data['total_enrollment']

        # Update term-specific block counts
        for term in ['fall', 'winter']:
            for size in [10, 20]:
                field = f'blocks_{size}_count_{term}'
                if field in data:
                    if not isinstance(data[field], int) or data[field] < 0:
                        return jsonify({'error': f'Invalid {field}'}), HTTPStatus.BAD_REQUEST
                    setattr(program, field, data[field])

        db.session.commit()

        return jsonify({
            'program_id': program.program_id,
            'program_name': program.program_name,
            'total_enrollment': program.total_enrollment,
            'blocks_20_count_fall': program.blocks_20_count_fall,
            'blocks_10_count_fall': program.blocks_10_count_fall,
            'blocks_20_count_winter': program.blocks_20_count_winter,
            'blocks_10_count_winter': program.blocks_10_count_winter
        }), HTTPStatus.OK
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR


@bp.route('/<program_id>', methods=['DELETE'], strict_slashes=False)
def delete_program(program_id):
    try:
        program = Program.query.get_or_404(program_id)
        
        # Delete associated blocks first
        Block.query.filter_by(program_id=program_id).delete()
        
        # Delete program requirements
        ProgramRequirement.query.filter_by(program_id=program_id).delete()
        
        # Delete the program
        db.session.delete(program)
        db.session.commit()
        
        return '', HTTPStatus.NO_CONTENT
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

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

@bp.route('/<program_id>/blocks', methods=['PATCH'])
def update_block_counts(program_id):
    try:
        program = Program.query.get_or_404(program_id)
        data = request.get_json()
        
        # Validate term
        term = data.get('term')
        if term not in ['FALL', 'WINTER']:
            return jsonify({'error': 'Invalid term'}), HTTPStatus.BAD_REQUEST
            
        # Update term-specific block counts
        term_suffix = term.lower()
        if f'blocks_20_count_{term_suffix}' in data:
            count = data[f'blocks_20_count_{term_suffix}']
            if not isinstance(count, int) or count < 0:
                return jsonify({'error': f'Invalid blocks_20_count_{term_suffix}'}), HTTPStatus.BAD_REQUEST
            setattr(program, f'blocks_20_count_{term_suffix}', count)
            
        if f'blocks_10_count_{term_suffix}' in data:
            count = data[f'blocks_10_count_{term_suffix}']
            if not isinstance(count, int) or count < 0:
                return jsonify({'error': f'Invalid blocks_10_count_{term_suffix}'}), HTTPStatus.BAD_REQUEST
            setattr(program, f'blocks_10_count_{term_suffix}', count)
            
        db.session.commit()
        
        return jsonify({
            'program_id': program.program_id,
            'blocks_20_count_fall': program.blocks_20_count_fall,
            'blocks_10_count_fall': program.blocks_10_count_fall,
            'blocks_20_count_winter': program.blocks_20_count_winter,
            'blocks_10_count_winter': program.blocks_10_count_winter
        }), HTTPStatus.OK
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR