# app/routes/course_offerings.py
from flask import Blueprint, jsonify, request
from app.models import CourseOffering, Course
from app import db
from http import HTTPStatus
from datetime import datetime

bp = Blueprint('offerings', __name__, url_prefix='/api/offerings')

@bp.route('/', methods=['GET'])
def get_offerings():
    offerings = CourseOffering.query.all()
    return jsonify([{
        'offering_id': o.offering_id,
        'course_id': o.course_id,
        'section_type': o.section_type,
        'section_code': o.section_code,
        'day_of_week': o.day_of_week,
        'start_time': o.start_time.strftime('%H:%M'),
        'end_time': o.end_time.strftime('%H:%M'),
        'capacity': o.capacity,
        'current_enrollment': o.current_enrollment,
        'term': o.term,
        'academic_year': o.academic_year,
        'status': o.status
    } for o in offerings]), HTTPStatus.OK

@bp.route('/<int:offering_id>', methods=['GET'])
def get_offering(offering_id):
    offering = CourseOffering.query.get_or_404(offering_id)
    return jsonify({
        'offering_id': offering.offering_id,
        'course_id': offering.course_id,
        'section_type': offering.section_type,
        'section_code': offering.section_code,
        'day_of_week': offering.day_of_week,
        'start_time': offering.start_time.strftime('%H:%M'),
        'end_time': offering.end_time.strftime('%H:%M'),
        'capacity': offering.capacity,
        'current_enrollment': offering.current_enrollment,
        'term': offering.term,
        'academic_year': offering.academic_year,
        'status': offering.status
    }), HTTPStatus.OK

@bp.route('/', methods=['POST'])
def create_offering():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['course_id', 'section_type', 'section_code', 'day_of_week', 
                         'start_time', 'end_time', 'capacity', 'term', 'academic_year']
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), HTTPStatus.BAD_REQUEST
            
        # Validate course exists
        if not Course.query.get(data['course_id']):
            return jsonify({'error': 'Course not found'}), HTTPStatus.NOT_FOUND
            
        # Convert time strings to Time objects
        try:
            data['start_time'] = datetime.strptime(data['start_time'], '%H:%M').time()
            data['end_time'] = datetime.strptime(data['end_time'], '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Invalid time format. Use HH:MM'}), HTTPStatus.BAD_REQUEST
            
        # Validate day_of_week
        if not 1 <= data['day_of_week'] <= 7:
            return jsonify({'error': 'day_of_week must be between 1 and 7'}), HTTPStatus.BAD_REQUEST
            
        offering = CourseOffering(**data)
        db.session.add(offering)
        db.session.commit()
        
        return jsonify({
            'offering_id': offering.offering_id,
            'course_id': offering.course_id,
            'section_type': offering.section_type,
            'section_code': offering.section_code,
            'day_of_week': offering.day_of_week,
            'start_time': offering.start_time.strftime('%H:%M'),
            'end_time': offering.end_time.strftime('%H:%M'),
            'capacity': offering.capacity,
            'current_enrollment': offering.current_enrollment,
            'term': offering.term,
            'academic_year': offering.academic_year,
            'status': offering.status
        }), HTTPStatus.CREATED
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<int:offering_id>', methods=['PUT'])
def update_offering(offering_id):
    offering = CourseOffering.query.get_or_404(offering_id)
    data = request.get_json()
    
    try:
        if 'start_time' in data:
            data['start_time'] = datetime.strptime(data['start_time'], '%H:%M').time()
        if 'end_time' in data:
            data['end_time'] = datetime.strptime(data['end_time'], '%H:%M').time()
            
        for field in ['section_type', 'section_code', 'day_of_week', 'capacity', 
                     'current_enrollment', 'term', 'academic_year', 'status']:
            if field in data:
                setattr(offering, field, data[field])
                
        db.session.commit()
        return jsonify({
            'offering_id': offering.offering_id,
            'course_id': offering.course_id,
            'section_type': offering.section_type,
            'section_code': offering.section_code,
            'day_of_week': offering.day_of_week,
            'start_time': offering.start_time.strftime('%H:%M'),
            'end_time': offering.end_time.strftime('%H:%M'),
            'capacity': offering.capacity,
            'current_enrollment': offering.current_enrollment,
            'term': offering.term,
            'academic_year': offering.academic_year,
            'status': offering.status
        }), HTTPStatus.OK
            
    except ValueError:
        return jsonify({'error': 'Invalid time format. Use HH:MM'}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<int:offering_id>', methods=['DELETE'])
def delete_offering(offering_id):
    offering = CourseOffering.query.get_or_404(offering_id)
    db.session.delete(offering)
    db.session.commit()
    return '', HTTPStatus.NO_CONTENT
