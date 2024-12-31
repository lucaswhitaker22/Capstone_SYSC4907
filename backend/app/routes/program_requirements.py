# app/routes/program_requirements.py
from flask import Blueprint, jsonify, request
from app.models import ProgramRequirement, Program, Course
from app import db
from http import HTTPStatus

bp = Blueprint('requirements', __name__, url_prefix='/api/requirements')

@bp.route('/program/<program_id>', methods=['GET'])
def get_program_requirements(program_id):
    try:
        if not Program.query.get(program_id):
            return jsonify({'error': 'Program not found'}), HTTPStatus.NOT_FOUND
            
        requirements = ProgramRequirement.query.filter_by(program_id=program_id).all()
        return jsonify([{
            'program_id': r.program_id,
            'course_id': r.course_id,
            'term': r.term
        } for r in requirements]), HTTPStatus.OK
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/', methods=['POST'])
def create_requirement():
    try:
        data = request.get_json()
        
        # Check for null data first
        if data is None:
            return jsonify({'error': 'No data provided'}), HTTPStatus.BAD_REQUEST
            
        # Rest of the validation logic
        required_fields = ['program_id', 'course_id', 'term']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), HTTPStatus.BAD_REQUEST
        
        # Validate term is a positive integer
        try:
            term = int(data['term'])
            if term <= 0:
                return jsonify({'error': 'Term must be a positive integer'}), HTTPStatus.BAD_REQUEST
            data['term'] = term
        except ValueError:
            return jsonify({'error': 'Term must be a valid integer'}), HTTPStatus.BAD_REQUEST

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
            'course_id': requirement.course_id, 
            'term': requirement.term
        }), HTTPStatus.CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<int:requirement_id>', methods=['PUT'])
def update_requirement(requirement_id):
    try:
        requirement = ProgramRequirement.query.get_or_404(requirement_id)
        data = request.get_json()
        
        if 'term' in data:
            requirement.term = data['term']
            
        if 'course_id' in data:
            if not Course.query.get(data['course_id']):
                return jsonify({'error': 'Course not found'}), HTTPStatus.NOT_FOUND
            requirement.course_id = data['course_id']
            
        db.session.commit()
        return jsonify({
            'program_id': requirement.program_id,
            'course_id': requirement.course_id,
            'term': requirement.term
        }), HTTPStatus.OK
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<int:requirement_id>', methods=['DELETE'])
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

@bp.route('/validate/<program_id>', methods=['POST'])
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
                if schedule.has_course(req.course_id) and schedule.term == req.term:
                    requirement_met = True
                    break
            if not requirement_met:
                missing_requirements.append({
                    'course_id': req.course_id,
                    'term': req.term
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