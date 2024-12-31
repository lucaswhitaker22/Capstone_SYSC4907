# app/routes/courses.py
from flask import Blueprint, jsonify, request
from app.models import Course
from app import db
from http import HTTPStatus

bp = Blueprint('courses', __name__, url_prefix='/api/courses')

@bp.route('/', methods=['GET'])
def get_courses():
    try:
        courses = Course.query.all()
        return jsonify([{
            'course_id': c.course_id,
            'course_name': c.course_name,
            'credits': float(c.credits)
        } for c in courses]), HTTPStatus.OK
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<course_id>', methods=['GET'])
def get_course(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        return jsonify({
            'course_id': course.course_id,
            'course_name': course.course_name,
            'credits': float(course.credits)
        }), HTTPStatus.OK
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/', methods=['POST'])
def create_course():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['course_id', 'course_name', 'credits']
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), HTTPStatus.BAD_REQUEST
            
        # Validate data types
        if not isinstance(data['credits'], (int, float)):
            return jsonify({'error': 'Credits must be a number'}), HTTPStatus.BAD_REQUEST
            
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
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<course_id>', methods=['PUT'])
def update_course(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), HTTPStatus.BAD_REQUEST
            
        if 'credits' in data and not isinstance(data['credits'], (int, float)):
            return jsonify({'error': 'Credits must be a number'}), HTTPStatus.BAD_REQUEST
            
        if 'course_name' in data:
            course.course_name = data['course_name']
        if 'credits' in data:
            course.credits = data['credits']
        
        db.session.commit()
        
        return jsonify({
            'course_id': course.course_id,
            'course_name': course.course_name,
            'credits': float(course.credits)
        }), HTTPStatus.OK
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        db.session.delete(course)
        db.session.commit()
        return '', HTTPStatus.NO_CONTENT
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR
