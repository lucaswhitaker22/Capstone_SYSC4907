# app/routes/courses.py
from flask import Blueprint, jsonify, request
from app.models import Course
from app import db
from http import HTTPStatus

bp = Blueprint('courses', __name__, url_prefix='/api/courses')

@bp.route('/', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify([{
        'course_id': c.course_id,
        'course_name': c.course_name,
        'credits': float(c.credits)
    } for c in courses]), HTTPStatus.OK

@bp.route('/<course_id>', methods=['GET'])
def get_course(course_id):
    course = Course.query.get_or_404(course_id)
    return jsonify({
        'course_id': course.course_id,
        'course_name': course.course_name,
        'credits': float(course.credits)
    }), HTTPStatus.OK

@bp.route('/', methods=['POST'])
def create_course():
    data = request.get_json()
    
    if Course.query.get(data['course_id']):
        return jsonify({'error': 'Course already exists'}), HTTPStatus.CONFLICT
    
    course = Course(
        course_id=data['course_id'],
        course_name=data['course_name'],
        credits=data['credits']
    )
    
    db.session.add(course)
    db.session.commit()
    
    return jsonify({
        'course_id': course.course_id,
        'course_name': course.course_name,
        'credits': float(course.credits)
    }), HTTPStatus.CREATED

@bp.route('/<course_id>', methods=['PUT'])
def update_course(course_id):
    course = Course.query.get_or_404(course_id)
    data = request.get_json()
    
    course.course_name = data.get('course_name', course.course_name)
    course.credits = data.get('credits', course.credits)
    
    db.session.commit()
    
    return jsonify({
        'course_id': course.course_id,
        'course_name': course.course_name,
        'credits': float(course.credits)
    }), HTTPStatus.OK

@bp.route('/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    return '', HTTPStatus.NO_CONTENT