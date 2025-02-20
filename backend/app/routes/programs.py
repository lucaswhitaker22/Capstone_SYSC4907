# app/routes/programs.py
from flask import Blueprint, jsonify, request
from app.models import Program, Block, ProgramRequirement, BlockSchedule,CourseOffering
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
            'blocks_10_count': p.blocks_10_count,

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
        
        required_fields = [
            'program_id', 'program_name', 'total_enrollment',
            'blocks_20_count', 'blocks_10_count', 'academic_year'
        ]
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), HTTPStatus.BAD_REQUEST

        program = Program(
            program_id=data['program_id'],
            program_name=data['program_name'],
            total_enrollment=data['total_enrollment'],
            blocks_20_count=data['blocks_20_count'],
            blocks_10_count=data['blocks_10_count']
        )
        db.session.add(program)
        
        # Generate identical blocks for both terms
        blocks = []
        for term, prefix in [('FALL', 'F'), ('WINTER', 'W')]:
            # 20-student blocks
            for i in range(data['blocks_20_count']):
                blocks.append(Block(
                    block_id=f"{data['program_id']}_{prefix}_20_{i+1}",
                    program_id=data['program_id'],
                    block_size=20,
                    term=term,
                    academic_year=data['academic_year'],
                    status="DRAFT"
                ))
            
            # 10-student blocks
            for i in range(data['blocks_10_count']):
                blocks.append(Block(
                    block_id=f"{data['program_id']}_{prefix}_10_{i+1}",
                    program_id=data['program_id'],
                    block_size=10,
                    term=term,
                    academic_year=data['academic_year'],
                    status="DRAFT"
                ))
        
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

    
@bp.route('/<program_id>', methods=['PUT'], strict_slashes=False)
def update_program(program_id):
    try:
        program = Program.query.get_or_404(program_id)
        data = request.get_json()
        
        if 'program_name' in data:
            program.program_name = data['program_name']
        if 'total_enrollment' in data:
            program.total_enrollment = data['total_enrollment']
        if 'blocks_20_count' in data:
            program.blocks_20_count = data['blocks_20_count']
        if 'blocks_10_count' in data:
            program.blocks_10_count = data['blocks_10_count']
            
        db.session.commit()
        
        return jsonify({
            'program_id': program.program_id,
            'program_name': program.program_name,
            'total_enrollment': program.total_enrollment,
            'blocks_20_count': program.blocks_20_count,
            'blocks_10_count': program.blocks_10_count
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
        
        # Get all blocks for the program
        blocks = Block.query.filter_by(program_id=program_id).all()
        
        # For each block, update course offering enrollments
        for block in blocks:
            schedules = BlockSchedule.query.filter_by(block_id=block.block_id).all()
            for schedule in schedules:
                offering = CourseOffering.query.get(schedule.offering_id)
                # Decrease enrollment by block size
                offering.current_enrollment -= block.block_size
                # Update offering status if no longer full
                if offering.current_enrollment < offering.capacity:
                    offering.status = 'OPEN'
        
        # Delete all block schedules first (due to foreign key constraints)
        for block in blocks:
            BlockSchedule.query.filter_by(block_id=block.block_id).delete()
            
        # Delete all blocks
        Block.query.filter_by(program_id=program_id).delete()
        
        # Delete program requirements
        ProgramRequirement.query.filter_by(program_id=program_id).delete()
        
        # Finally delete the program
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

@bp.route('/blocks', methods=['PATCH'])
def update_block_counts(program_id):
    try:
        program = Program.query.get_or_404(program_id)
        data = request.get_json()
        
        # Validate term
        term = data.get('term')
        if term not in ['FALL', 'WINTER']:
            return jsonify({'error': 'Invalid term'}), HTTPStatus.BAD_REQUEST
            
        term_suffix = term.lower()
        term_prefix = 'F' if term == 'FALL' else 'W'
        
        # Update 20-student blocks
        if f'blocks_20_count_{term_suffix}' in data:
            new_count = data[f'blocks_20_count_{term_suffix}']
            if not isinstance(new_count, int) or new_count < 0:
                return jsonify({'error': f'Invalid blocks_20_count_{term_suffix}'}), HTTPStatus.BAD_REQUEST
                
            # Delete existing blocks
            Block.query.filter_by(
                program_id=program_id,
                term=term,
                block_size=20
            ).delete()
            
            # Create new blocks
            for i in range(new_count):
                block = Block(
                    block_id=f"{program_id}_{term_prefix}_20_{i+1}",
                    program_id=program_id,
                    block_size=20,
                    term=term,
                    academic_year=data.get('academic_year', '2025-2026'),
                    status="DRAFT"
                )
                db.session.add(block)
            
            setattr(program, f'blocks_20_count_{term_suffix}', new_count)
            
        # Update 10-student blocks
        if f'blocks_10_count_{term_suffix}' in data:
            new_count = data[f'blocks_10_count_{term_suffix}']
            if not isinstance(new_count, int) or new_count < 0:
                return jsonify({'error': f'Invalid blocks_10_count_{term_suffix}'}), HTTPStatus.BAD_REQUEST
                
            # Delete existing blocks
            Block.query.filter_by(
                program_id=program_id,
                term=term,
                block_size=10
            ).delete()
            
            # Create new blocks
            for i in range(new_count):
                block = Block(
                    block_id=f"{program_id}_{term_prefix}_10_{i+1}",
                    program_id=program_id,
                    block_size=10,
                    term=term,
                    academic_year=data.get('academic_year', '2025-2026'),
                    status="DRAFT"
                )
                db.session.add(block)
                
            setattr(program, f'blocks_10_count_{term_suffix}', new_count)
        
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
