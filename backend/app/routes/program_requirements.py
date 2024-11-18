# app/routes/program_requirements.py
from flask import Blueprint, jsonify, request
from app.models import ProgramRequirement
from app import db
from http import HTTPStatus

bp = Blueprint('requirements', __name__, url_prefix='/api/requirements')

@bp.route('/program/<program_id>', methods=['GET'])
def get_program_requirements(program_id):
    requirements = ProgramRequirement.query.filter_by(program_id=program_id).all()
    return jsonify([{
        'program_id': r.program_id,
        'course_id': r.course_id,
        'term': r.term
    } for r in requirements]), HTTPStatus.OK

@bp.route('/', methods=['POST'])
def create_requirement():
    data = request.get_json()
    requirement = ProgramRequirement(**data)
    db.session.add(requirement)
    db.session.commit()
    
    return jsonify({
        'program_id': requirement.program_id,
        'course_id': requirement.course_id,
        'term': requirement.term
    }), HTTPStatus.CREATED