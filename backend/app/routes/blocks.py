# app/routes/blocks.py
from flask import Blueprint, jsonify, request
from app.models import Block, BlockSchedule
from app import db
from http import HTTPStatus

bp = Blueprint('blocks', __name__, url_prefix='/api/blocks')

@bp.route('/', methods=['GET'])
def get_blocks():
    blocks = Block.query.all()
    return jsonify([{
        'block_id': b.block_id,
        'program_id': b.program_id,
        'block_size': b.block_size,
        'term': b.term,
        'academic_year': b.academic_year,
        'schedule_rating': float(b.schedule_rating) if b.schedule_rating else None,
        'status': b.status
    } for b in blocks]), HTTPStatus.OK

@bp.route('/<block_id>', methods=['GET'])
def get_block(block_id):
    block = Block.query.get_or_404(block_id)
    return jsonify({
        'block_id': block.block_id,
        'program_id': block.program_id,
        'block_size': block.block_size,
        'term': block.term,
        'academic_year': block.academic_year,
        'schedule_rating': float(block.schedule_rating) if block.schedule_rating else None,
        'early_starts': block.early_starts,
        'late_ends': block.late_ends,
        'long_breaks': block.long_breaks,
        'consecutive_days': block.consecutive_days,
        'status': block.status
    }), HTTPStatus.OK

@bp.route('/', methods=['POST'])
def create_block():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['block_id', 'program_id', 'block_size', 'term', 'academic_year']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), HTTPStatus.BAD_REQUEST
        
    # Validate block size before attempting insert
    if data['block_size'] not in (10, 20):
        return jsonify({'error': 'Block size must be 10 or 20'}), HTTPStatus.BAD_REQUEST
        
    # Check if block already exists
    if Block.query.get(data['block_id']):
        return jsonify({'error': 'Block already exists'}), HTTPStatus.CONFLICT
        
    try:
        block = Block(**data)
        db.session.add(block)
        db.session.commit()
        
        return jsonify({
            'block_id': block.block_id,
            'program_id': block.program_id,
            'block_size': block.block_size,
            'term': block.term,
            'academic_year': block.academic_year,
            'status': block.status
        }), HTTPStatus.CREATED
        
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Invalid block data'}), HTTPStatus.BAD_REQUEST

@bp.route('/<block_id>/status', methods=['PATCH'])
def update_block_status(block_id):
    try:
        block = Block.query.get_or_404(block_id)
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({'error': 'Status is required'}), HTTPStatus.BAD_REQUEST
            
        # Validate status value
        valid_statuses = ['DRAFT', 'PUBLISHED', 'LOCKED']
        if data['status'] not in valid_statuses:
            return jsonify({'error': f'Status must be one of: {", ".join(valid_statuses)}'}), HTTPStatus.BAD_REQUEST
            
        block.status = data['status']
        db.session.commit()
        
        return jsonify({
            'block_id': block.block_id,
            'status': block.status
        }), HTTPStatus.OK
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<block_id>', methods=['PUT'])
def update_block(block_id):
    try:
        block = Block.query.get_or_404(block_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), HTTPStatus.BAD_REQUEST
            
        # Validate block size if provided
        if 'block_size' in data and data['block_size'] not in (10, 20):
            return jsonify({'error': 'Block size must be 10 or 20'}), HTTPStatus.BAD_REQUEST
            
        # Update fields if provided
        updateable_fields = ['program_id', 'block_size', 'term', 'academic_year', 'status']
        for field in updateable_fields:
            if field in data:
                setattr(block, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'block_id': block.block_id,
            'program_id': block.program_id,
            'block_size': block.block_size,
            'term': block.term,
            'academic_year': block.academic_year,
            'status': block.status
        }), HTTPStatus.OK
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<block_id>', methods=['DELETE'])
def delete_block(block_id):
    try:
        block = Block.query.get_or_404(block_id)
        
        # Check if block can be deleted (not LOCKED)
        if block.status == 'LOCKED':
            return jsonify({
                'error': 'Cannot delete locked block'
            }), HTTPStatus.FORBIDDEN

        # Delete associated block schedules first
        BlockSchedule.query.filter_by(block_id=block_id).delete()
        
        # Delete the block
        db.session.delete(block)
        db.session.commit()
        
        return '', HTTPStatus.NO_CONTENT

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<block_id>/rating', methods=['POST'])
def calculate_block_rating(block_id):
    try:
        block = Block.query.get_or_404(block_id)
        schedules = BlockSchedule.query.filter_by(block_id=block_id).all()
        
        # Initialize counters
        early_starts = 0
        late_ends = 0
        long_breaks = 0
        consecutive_days = set()
        
        # Get all offerings for the block
        offerings = [schedule.course_offering for schedule in schedules]
        
        for offering in offerings:
            # Check for early starts (before 8:30)
            if offering.start_time < time.fromisoformat('08:30'):
                early_starts += 1
                
            # Check for late ends (after 17:30)
            if offering.end_time > time.fromisoformat('17:30'):
                late_ends += 1
                
            # Add day to consecutive days set
            consecutive_days.add(offering.day_of_week)
            
        # Sort offerings by day and time to check for breaks
        offerings.sort(key=lambda x: (x.day_of_week, x.start_time))
        
        # Check for long breaks (> 2 hours) between classes on same day
        for i in range(len(offerings)-1):
            if (offerings[i].day_of_week == offerings[i+1].day_of_week and 
                (offerings[i+1].start_time.hour - offerings[i].end_time.hour) > 2):
                long_breaks += 1
        
        # Calculate consecutive days penalty
        consecutive_days_count = 0
        days = sorted(list(consecutive_days))
        for i in range(len(days)-1):
            if days[i+1] - days[i] == 1:
                consecutive_days_count += 1
        
        # Update block ratings
        block.early_starts = early_starts
        block.late_ends = late_ends
        block.long_breaks = long_breaks
        block.consecutive_days = consecutive_days_count
        
        # Calculate overall rating (0-100 scale)
        total_penalties = early_starts + late_ends + long_breaks + consecutive_days_count
        max_penalties = len(offerings)  # Maximum possible penalties per category
        if max_penalties > 0:
            block.schedule_rating = max(0, 100 - (total_penalties / max_penalties) * 25)
        else:
            block.schedule_rating = 100
        
        db.session.commit()
        
        return jsonify({
            'block_id': block.block_id,
            'schedule_rating': float(block.schedule_rating),
            'early_starts': block.early_starts,
            'late_ends': block.late_ends,
            'long_breaks': block.long_breaks,
            'consecutive_days': block.consecutive_days
        }), HTTPStatus.OK
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR
