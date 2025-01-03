from flask import Blueprint, jsonify, request, current_app
from app.models import BlockSchedule, Block, CourseOffering, ProgramRequirement, Program
from app.database import db
from app.routes.utils.schedule_generator import generate_block_schedule, rate_block_schedule
from app.routes.utils.schedule_validator import validate_block_schedule
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
    
@bp.route('/block/<block_id>/generate', methods=['POST'])
def generate(block_id):
    return generate_block_schedule(block_id)


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
def validate(block_id):
    return validate_block_schedule(block_id)

@bp.route('/block/<block_id>/rate', methods=['GET'])
def rate(block_id):
    return rate_block_schedule(block_id)

@bp.route('/program/<program_id>/schedules', methods=['GET'])
def get_all_possible_schedules(program_id):
    try:
        # Validate program exists
        program = Program.query.get_or_404(program_id)
        
        # Get program requirements
        program_requirements = ProgramRequirement.query.filter_by(
            program_id=program_id
        ).order_by(ProgramRequirement.requirement_id).all()

        if not program_requirements:
            return jsonify({
                'error': 'No requirements found for program'
            }), HTTPStatus.NOT_FOUND

        # Get required course IDs
        required_courses = [req.course_id for req in program_requirements]

        # Get all available offerings for required courses
        available_offerings = CourseOffering.query.filter(
            CourseOffering.course_id.in_(required_courses)
        ).all()

        # Group offerings by course
        course_offerings = {}
        for offering in available_offerings:
            if offering.course_id not in course_offerings:
                course_offerings[offering.course_id] = {'LECTURE': [], 'LAB': [], 'TUTORIAL': []}
            course_offerings[offering.course_id][offering.section_type].append(offering)

        valid_schedules = []

        def try_schedule_combination(current_schedule, remaining_courses):
            if not remaining_courses:
                valid_schedules.append(current_schedule.copy())
                return

            current_course = remaining_courses[0]
            if current_course not in course_offerings:
                return

            # Group lectures by their section prefix
            lecture_groups = {}
            for lecture in course_offerings[current_course]['LECTURE']:
                prefix = lecture.section_code.split('-')[0]
                if prefix not in lecture_groups:
                    lecture_groups[prefix] = []
                lecture_groups[prefix].append(lecture)

            # Try each lecture group
            for prefix, lectures in lecture_groups.items():
                all_lectures_fit = True
                temp_schedule = current_schedule.copy()

                # Add all lectures from this section group
                for lecture in lectures:
                    if any(has_time_conflict(lecture, selected) for selected in temp_schedule):
                        all_lectures_fit = False
                        break
                    temp_schedule.append(lecture)

                if all_lectures_fit:
                    if course_offerings[current_course]['LAB']:
                        # Try each lab with this lecture group
                        for lab in course_offerings[current_course]['LAB']:
                            if not any(has_time_conflict(lab, selected) for selected in temp_schedule):
                                try_schedule_combination(
                                    temp_schedule + [lab],
                                    remaining_courses[1:]
                                )
                    else:
                        # No lab required, continue with next course
                        try_schedule_combination(
                            temp_schedule,
                            remaining_courses[1:]
                        )

        # Generate all possible schedules
        try_schedule_combination([], required_courses)

        # Format response
        formatted_schedules = []
        for schedule in valid_schedules:
            formatted_offerings = [{
                'offering_id': o.offering_id,
                'course_id': o.course_id,
                'requirement_id': next(
                    (r.requirement_id for r in program_requirements if r.course_id == o.course_id),
                    None
                ),
                'section_type': o.section_type,
                'section_code': o.section_code,
                'day_of_week': o.day_of_week,
                'start_time': o.start_time.strftime('%H:%M'),
                'end_time': o.end_time.strftime('%H:%M')
            } for o in schedule]
            formatted_schedules.append(formatted_offerings)

        return jsonify({
            'program_id': program_id,
            'total_schedules': len(formatted_schedules),
            'schedules': formatted_schedules
        }), HTTPStatus.OK

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR
