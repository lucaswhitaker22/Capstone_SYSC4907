# app/routes/block_schedules.py
from flask import Blueprint, jsonify, request
from app.models import BlockSchedule, Block, CourseOffering
from app import db
from http import HTTPStatus

bp = Blueprint('schedules', __name__, url_prefix='/api/schedules')

@bp.route('/block/<block_id>', methods=['POST'])
def add_offering_to_block(block_id):
    data = request.get_json()
    
    block = Block.query.get_or_404(block_id)
    offering = CourseOffering.query.get_or_404(data['offering_id'])
    
    # Check for scheduling conflicts
    existing_schedules = BlockSchedule.query.filter_by(block_id=block_id).all()
    for schedule in existing_schedules:
        if (schedule.course_offering.day_of_week == offering.day_of_week and
            ((offering.start_time >= schedule.course_offering.start_time and 
              offering.start_time < schedule.course_offering.end_time) or
             (offering.end_time > schedule.course_offering.start_time and 
              offering.end_time <= schedule.course_offering.end_time))):
            return jsonify({'error': 'Time conflict detected'}), HTTPStatus.CONFLICT
    
    block_schedule = BlockSchedule(block_id=block_id, offering_id=offering.offering_id)
    db.session.add(block_schedule)
    db.session.commit()
    
    return jsonify({
        'block_id': block_schedule.block_id,
        'offering_id': block_schedule.offering_id
    }), HTTPStatus.CREATED

@bp.route('/block/<block_id>/offering/<offering_id>', methods=['DELETE'])
def remove_offering_from_block(block_id, offering_id):
    schedule = BlockSchedule.query.filter_by(
        block_id=block_id, 
        offering_id=offering_id
    ).first_or_404()
    
    db.session.delete(schedule)
    db.session.commit()
    
    return '', HTTPStatus.NO_CONTENT