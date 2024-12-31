# app/routes/program_requirements.py
from flask import Blueprint, jsonify, request
from app.models import ProgramRequirement, Program, Course
from app import db
from http import HTTPStatus

bp = Blueprint('requirements', __name__, url_prefix='/api/requirements')

@bp.route('/program/<program_id>', methods=['GET'])
def get_program_requirements(program_id):
    try:
        # Verify program exists
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
        
        # Validate required fields
        required_fields = ['program_id', 'course_id', 'term']
        if not data or not all(field in data for field in required_fields):
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
            'course_id': requirement.course_id,
            'term': requirement.term
        }), HTTPStatus.CREATED
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

