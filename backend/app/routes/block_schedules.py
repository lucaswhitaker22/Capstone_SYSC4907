from flask import Blueprint, jsonify, request, current_app
from app.models import BlockSchedule, Block, CourseOffering
from app.database import db
from http import HTTPStatus
from .conflicts import has_time_conflict
import logging

bp = Blueprint('schedules', __name__, url_prefix='/api/schedules')

@bp.route('/block/<block_id>', methods=['GET'], strict_slashes=False)
def get_block_schedule(block_id):
    try:
        block = Block.query.get(block_id)
        if not block:
            return jsonify({
                'error': 'Not Found',
                'message': f'Block {block_id} not found'
            }), HTTPStatus.NOT_FOUND
            
        schedules = BlockSchedule.query.filter_by(block_id=block_id).all()
        offerings = []
        for schedule in schedules:
            offering = schedule.course_offering
            offerings.append({
                'offering_id': offering.offering_id,
                'course_id': offering.course_id,
                'section_type': offering.section_type,
                'section_code': offering.section_code,
                'day_of_week': offering.day_of_week,
                'start_time': offering.start_time.strftime('%H:%M'),
                'end_time': offering.end_time.strftime('%H:%M')
            })
        return jsonify(offerings), HTTPStatus.OK
    except Exception as e:
        current_app.logger.error(f"Error getting block schedule: {str(e)}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/block/<block_id>', methods=['DELETE'], strict_slashes=False)
def delete_block_schedule(block_id):
    try:
        # Check if block exists
        block = Block.query.get_or_404(block_id)
        
        # Check if block is locked
        if block.status == 'LOCKED':
            return jsonify({
                'error': 'Cannot delete schedule of locked block'
            }), HTTPStatus.FORBIDDEN

        # Delete all schedule entries for the block
        BlockSchedule.query.filter_by(block_id=block_id).delete()
        db.session.commit()
        
        return '', HTTPStatus.NO_CONTENT

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR


@bp.route('/block/<block_id>', methods=['POST'], strict_slashes=False)
def add_offering_to_block(block_id):
    try:
        data = request.get_json()
        if not data or 'offering_id' not in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'offering_id is required'
            }), HTTPStatus.BAD_REQUEST

        current_app.logger.info(f"Adding offering to block: {block_id}, offering_id: {data['offering_id']}")
        
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
        
        # Get existing offerings in block
        existing_schedules = BlockSchedule.query.filter_by(block_id=block_id).all()
        existing_offerings = [schedule.course_offering for schedule in existing_schedules]
        
        # Check for conflicts using the conflicts module
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
        current_app.logger.error(f"Error adding offering to block: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR
    
@bp.route('/block/<block_id>/generate', methods=['POST'], strict_slashes=False)
def generate_block_schedule(block_id):
    try:
        # Get block and validate
        block = Block.query.get_or_404(block_id)
        if block.status == 'LOCKED':
            return jsonify({
                'error': 'Cannot modify locked block'
            }), HTTPStatus.FORBIDDEN

        # Clear existing schedule
        BlockSchedule.query.filter_by(block_id=block_id).delete()
        db.session.commit()

        # Get available offerings for the term
        available_offerings = CourseOffering.query.filter_by(
            term=block.term,
            academic_year=block.academic_year,
            status='OPEN'
        ).all()

        # Generate schedule
        selected_offerings = []
        for offering in available_offerings:
            # Check conflicts with already selected offerings
            has_conflicts = any(
                has_time_conflict(offering, selected) 
                for selected in selected_offerings
            )
            
            if not has_conflicts:
                selected_offerings.append(offering)
                block_schedule = BlockSchedule(
                    block_id=block_id,
                    offering_id=offering.offering_id
                )
                db.session.add(block_schedule)

            if len(selected_offerings) >= block.block_size:
                break

        db.session.commit()

        # Return formatted response matching frontend expectations
        formatted_offerings = [{
            'offering_id': o.offering_id,
            'course_id': o.course_id,
            'section_type': o.section_type,
            'section_code': o.section_code,
            'day_of_week': o.day_of_week,
            'start_time': o.start_time.strftime('%H:%M'),
            'end_time': o.end_time.strftime('%H:%M')
        } for o in selected_offerings]

        return jsonify(formatted_offerings), HTTPStatus.CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

    
@bp.route('/block/<block_id>/offering/<offering_id>', methods=['DELETE'], strict_slashes=False)
def remove_offering_from_block(block_id, offering_id):
    try:
        schedule = BlockSchedule.query.filter_by(
            block_id=block_id,
            offering_id=offering_id
        ).first()
        
        if not schedule:
            return jsonify({
                'error': 'Not Found',
                'message': 'Schedule entry not found'
            }), HTTPStatus.NOT_FOUND
            
        db.session.delete(schedule)
        db.session.commit()
        
        return '', HTTPStatus.NO_CONTENT
    except Exception as e:
        current_app.logger.error(f"Error removing offering from block: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/block/<block_id>/validate', methods=['GET'], strict_slashes=False)
def validate_block_schedule(block_id):
    try:
        schedules = BlockSchedule.query.filter_by(block_id=block_id).all()
        offerings = [schedule.course_offering for schedule in schedules]
        
        conflicts = []
        for i, offering1 in enumerate(offerings):
            for offering2 in offerings[i+1:]:
                if has_time_conflict(offering1, offering2):
                    conflicts.append({
                        'offering1_id': offering1.offering_id,
                        'offering1_course': offering1.course_id,
                        'offering2_id': offering2.offering_id,
                        'offering2_course': offering2.course_id,
                        'day_of_week': offering1.day_of_week
                    })
        
        return jsonify({
            'valid': len(conflicts) == 0,
            'conflicts': conflicts
        }), HTTPStatus.OK
    except Exception as e:
        current_app.logger.error(f"Error validating block schedule: {str(e)}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR