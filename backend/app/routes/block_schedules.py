# app/routes/block_schedules.py
from flask import Blueprint, jsonify, request, current_app
from app.models import BlockSchedule, Block, CourseOffering
from app.database import db
from http import HTTPStatus
import logging

bp = Blueprint('schedules', __name__, url_prefix='/api/schedules')

@bp.route('/block/<block_id>', methods=['POST'])
def add_offering_to_block(block_id):
    try:
        data = request.get_json()
        if not data or 'offering_id' not in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'offering_id is required'
            }), HTTPStatus.BAD_REQUEST

        # Log the incoming request
        current_app.logger.info(f"Adding offering to block: {block_id}, offering_id: {data['offering_id']}")
        
        # Check if block exists
        block = Block.query.get(block_id)
        if not block:
            return jsonify({
                'error': 'Not Found',
                'message': f'Block {block_id} not found'
            }), HTTPStatus.NOT_FOUND

        # Check if offering exists
        offering = CourseOffering.query.get(data['offering_id'])
        if not offering:
            return jsonify({
                'error': 'Not Found',
                'message': f'Offering {data["offering_id"]} not found'
            }), HTTPStatus.NOT_FOUND
        
        # Check for scheduling conflicts
        existing_schedules = BlockSchedule.query.filter_by(block_id=block_id).all()
        for schedule in existing_schedules:
            if (schedule.course_offering.day_of_week == offering.day_of_week and
                ((offering.start_time >= schedule.course_offering.start_time and 
                  offering.start_time < schedule.course_offering.end_time) or
                 (offering.end_time > schedule.course_offering.start_time and 
                  offering.end_time <= schedule.course_offering.end_time))):
                return jsonify({
                    'error': 'Conflict',
                    'message': 'Time conflict detected'
                }), HTTPStatus.CONFLICT
        
        block_schedule = BlockSchedule(block_id=block_id, offering_id=offering.offering_id)
        db.session.add(block_schedule)
        db.session.commit()
        
        return jsonify({
            'block_id': block_schedule.block_id,
            'offering_id': block_schedule.offering_id
        }), HTTPStatus.CREATED

    except Exception as e:
        current_app.logger.error(f"Error adding offering to block: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR