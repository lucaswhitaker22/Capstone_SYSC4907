# app/routes/programs.py
from flask import Blueprint, jsonify, request
from app.models import Program
from app import db
from http import HTTPStatus

bp = Blueprint('programs', __name__, url_prefix='/api/programs')

@bp.route('/', methods=['GET'])
def get_programs():
    programs = Program.query.all()
    return jsonify([{
        'program_id': p.program_id,
        'program_name': p.program_name,
        'total_enrollment': p.total_enrollment,
        'blocks_20_count': p.blocks_20_count,
        'blocks_10_count': p.blocks_10_count
    } for p in programs]), HTTPStatus.OK

@bp.route('/<program_id>', methods=['GET'])
def get_program(program_id):
    program = Program.query.get_or_404(program_id)
    return jsonify({
        'program_id': program.program_id,
        'program_name': program.program_name,
        'total_enrollment': program.total_enrollment,
        'blocks_20_count': program.blocks_20_count,
        'blocks_10_count': program.blocks_10_count
    }), HTTPStatus.OK

@bp.route('/', methods=['POST'])
def create_program():
    data = request.get_json()
    
    if Program.query.get(data['program_id']):
        return jsonify({'error': 'Program already exists'}), HTTPStatus.CONFLICT
    
    program = Program(**data)
    db.session.add(program)
    db.session.commit()
    
    return jsonify({
        'program_id': program.program_id,
        'program_name': program.program_name,
        'total_enrollment': program.total_enrollment,
        'blocks_20_count': program.blocks_20_count,
        'blocks_10_count': program.blocks_10_count
    }), HTTPStatus.CREATED