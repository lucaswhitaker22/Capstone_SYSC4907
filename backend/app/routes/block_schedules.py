# app/routes/schedules.py
from flask import Blueprint, jsonify, request, current_app
from app.models import BlockSchedule, Block, CourseOffering
from app import db
from http import HTTPStatus
from .conflicts import has_time_conflict

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

        # Check if block exists
        block = Block.query.get(block_id)
        if not block:
            return jsonify({
                'error': 'Not Found',
                'message': f'Block {block_id} not found'
            }), HTTPStatus.NOT_FOUND

        # Check if offering exists
        new_offering = CourseOffering.query.get(data['offering_id'])
        if not new_offering:
            return jsonify({
                'error': 'Not Found',
                'message': f'Offering {data["offering_id"]} not found'
            }), HTTPStatus.NOT_FOUND
        
        # Check if offering already in block
        existing_schedule = BlockSchedule.query.filter_by(
            block_id=block_id, 
            offering_id=data['offering_id']
        ).first()
        if existing_schedule:
            return jsonify({
                'error': 'Conflict',
                'message': 'Offering already exists in block'
            }), HTTPStatus.CONFLICT

        # Get existing offerings in block
        existing_schedules = BlockSchedule.query.filter_by(block_id=block_id).all()
        existing_offerings = [schedule.course_offering for schedule in existing_schedules]
        
        # Check for time conflicts
        conflicts = []
        for existing_offering in existing_offerings:
            if has_time_conflict(existing_offering, new_offering):
                conflicts.append({
                    'existing_offering_id': existing_offering.offering_id,
                    'existing_course_id': existing_offering.course_id,
                    'existing_time': f"{existing_offering.start_time.strftime('%H:%M')}-{existing_offering.end_time.strftime('%H:%M')}",
                    'new_offering_id': new_offering.offering_id,
                    'new_course_id': new_offering.course_id,
                    'new_time': f"{new_offering.start_time.strftime('%H:%M')}-{new_offering.end_time.strftime('%H:%M')}",
                    'day_of_week': new_offering.day_of_week
                })
        
        if conflicts:
            return jsonify({
                'error': 'Conflict',
                'message': 'Time conflicts detected',
                'conflicts': conflicts
            }), HTTPStatus.CONFLICT
        
        block_schedule = BlockSchedule(block_id=block_id, offering_id=new_offering.offering_id)
        db.session.add(block_schedule)
        db.session.commit()
        
        return jsonify({
            'block_id': block_schedule.block_id,
            'offering_id': block_schedule.offering_id,
            'course_id': new_offering.course_id,
            'section_type': new_offering.section_type,
            'section_code': new_offering.section_code,
            'day_of_week': new_offering.day_of_week,
            'start_time': new_offering.start_time.strftime('%H:%M'),
            'end_time': new_offering.end_time.strftime('%H:%M')
        }), HTTPStatus.CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR
