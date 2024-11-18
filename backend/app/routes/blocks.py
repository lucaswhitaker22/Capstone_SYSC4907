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

@bp.route('/<block_id>/schedule', methods=['GET'])
def get_block_schedule(block_id):
    block_schedules = BlockSchedule.query.filter_by(block_id=block_id).all()
    return jsonify([{
        'offering_id': bs.offering_id,
        'course_id': bs.course_offering.course_id,
        'section_type': bs.course_offering.section_type,
        'section_code': bs.course_offering.section_code,
        'day_of_week': bs.course_offering.day_of_week,
        'start_time': bs.course_offering.start_time.strftime('%H:%M'),
        'end_time': bs.course_offering.end_time.strftime('%H:%M')
    } for bs in block_schedules]), HTTPStatus.OK