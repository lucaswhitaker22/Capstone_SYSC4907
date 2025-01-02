# app/routes/program_requirements.py
from flask import Blueprint, jsonify, request
from app.models import ProgramRequirement, Program, Course, BlockSchedule
from app import db
from http import HTTPStatus

bp = Blueprint('requirements', __name__, url_prefix='/api/requirements')

@bp.route('/program/<program_id>', methods=['GET'], strict_slashes=False)
def get_program_requirements(program_id):
    try:
        if not Program.query.get(program_id):
            return jsonify({'error': 'Program not found'}), HTTPStatus.NOT_FOUND
            
        requirements = ProgramRequirement.query.filter_by(program_id=program_id).all()
        return jsonify([{
            'program_id': r.program_id,
            'course_id': r.course_id
        } for r in requirements]), HTTPStatus.OK
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/', methods=['POST'], strict_slashes=False)
def create_requirement():
    try:
        data = request.get_json()
        
        if data is None:
            return jsonify({'error': 'No data provided'}), HTTPStatus.BAD_REQUEST
            
        required_fields = ['program_id', 'course_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), HTTPStatus.BAD_REQUEST

        # Validate program exists
        if not Program.query.get(data['program_id']):
            return jsonify({'error': 'Program not found'}), HTTPStatus.NOT_FOUND

        # Validate course exists  
        if not Course.query.get(data['course_id']):
            return jsonify({'error': 'Course not found'}), HTTPStatus.NOT_FOUND

        # Check for duplicate requirement
        existing = ProgramRequirement.query.filter_by(
            program_id=data['program_id'],
            course_id=data['course_id']
        ).first()
        if existing:
            return jsonify({'error': 'Requirement already exists'}), HTTPStatus.CONFLICT

        requirement = ProgramRequirement(**data)
        db.session.add(requirement)
        db.session.commit()

        return jsonify({
            'program_id': requirement.program_id,
            'course_id': requirement.course_id
        }), HTTPStatus.CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<int:requirement_id>', methods=['PUT'], strict_slashes=False)
def update_requirement(requirement_id):
    try:
        requirement = ProgramRequirement.query.get_or_404(requirement_id)
        data = request.get_json()
            
        if 'course_id' in data:
            if not Course.query.get(data['course_id']):
                return jsonify({'error': 'Course not found'}), HTTPStatus.NOT_FOUND
            requirement.course_id = data['course_id']
            
        db.session.commit()
        return jsonify({
            'program_id': requirement.program_id,
            'course_id': requirement.course_id,
        }), HTTPStatus.OK
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<int:requirement_id>', methods=['DELETE'], strict_slashes=False)
def delete_requirement(requirement_id):
    try:
        requirement = ProgramRequirement.query.get_or_404(requirement_id)
        db.session.delete(requirement)
        db.session.commit()
        return '', HTTPStatus.NO_CONTENT
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/validate/<program_id>', methods=['POST'], strict_slashes=False)
def validate_program_schedule(program_id):
    try:
        program = Program.query.get_or_404(program_id)
        data = request.get_json()
        schedule_ids = data.get('schedule_ids', [])
        
        if not schedule_ids:
            return jsonify({'error': 'No schedules provided'}), HTTPStatus.BAD_REQUEST
            
        requirements = ProgramRequirement.query.filter_by(program_id=program_id).all()
        schedules = BlockSchedule.query.filter(BlockSchedule.schedule_id.in_(schedule_ids)).all()
        
        missing_requirements = []
        for req in requirements:
            requirement_met = False
            for schedule in schedules:
                if schedule.has_course(req.course_id):
                    requirement_met = True
                    break
            if not requirement_met:
                missing_requirements.append({
                    'course_id': req.course_id,
                })
        
        return jsonify({
            'program_id': program_id,
            'is_valid': len(missing_requirements) == 0,
            'missing_requirements': missing_requirements
        }), HTTPStatus.OK
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR