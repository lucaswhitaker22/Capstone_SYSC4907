# app/routes/course_offerings.py
from flask import Blueprint, jsonify, request
from app.models import CourseOffering
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

@bp.route('/', methods=['POST'])
def create_offering():
    data = request.get_json()
    
    # Convert time strings to Time objects
    data['start_time'] = datetime.strptime(data['start_time'], '%H:%M').time()
    data['end_time'] = datetime.strptime(data['end_time'], '%H:%M').time()
    
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