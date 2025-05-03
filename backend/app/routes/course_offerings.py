# app/routes/course_offerings.py
from flask import Blueprint, jsonify, request
from app.models import CourseOffering, Course, BlockSchedule
from app import db
from http import HTTPStatus
from datetime import datetime
import re
bp = Blueprint('offerings', __name__, url_prefix='/api/offerings')

@bp.route('/', methods=['GET'], strict_slashes=False)
def get_offerings():
    # Add term and year filtering
    term = request.args.get('term')
    academic_year = request.args.get('academic_year', '')
    
    query = CourseOffering.query
    
    if term:
        if term not in ['FALL', 'WINTER']:
            return jsonify({'error': 'Invalid term'}), HTTPStatus.BAD_REQUEST
        query = query.filter_by(term=term)
    
    if academic_year:
        query = query.filter_by(academic_year=academic_year)
        
    offerings = query.all()
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


@bp.route('/<int:offering_id>', methods=['GET'], strict_slashes=False)
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

@bp.route('/', methods=['POST'], strict_slashes=False)
def create_offering():
    try:
        data = request.get_json()
        
        required_fields = ['course_id', 'section_type', 'section_code', 'day_of_week', 
                         'start_time', 'end_time', 'capacity', 'term', 'academic_year']
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), HTTPStatus.BAD_REQUEST
            
        # Validate term
        if data['term'] not in ['FALL', 'WINTER']:
            return jsonify({'error': 'Invalid term'}), HTTPStatus.BAD_REQUEST
            
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
            
        # Check for duplicate section in same term
        existing = CourseOffering.query.filter_by(
            course_id=data['course_id'],
            section_code=data['section_code'],
            term=data['term'],
            academic_year=data['academic_year']
        ).first()
        
        if existing:
            return jsonify({'error': 'Section already exists for this term'}), HTTPStatus.CONFLICT
            
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

@bp.route('/<int:offering_id>', methods=['PUT'], strict_slashes=False)
def update_offering(offering_id):
    try:
        offering = CourseOffering.query.get_or_404(offering_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), HTTPStatus.BAD_REQUEST
            
        # Convert time strings if provided
        if 'start_time' in data:
            try:
                data['start_time'] = datetime.strptime(data['start_time'], '%H:%M').time()
            except ValueError:
                return jsonify({'error': 'Invalid start_time format. Use HH:MM'}), HTTPStatus.BAD_REQUEST
                
        if 'end_time' in data:
            try:
                data['end_time'] = datetime.strptime(data['end_time'], '%H:%M').time()
            except ValueError:
                return jsonify({'error': 'Invalid end_time format. Use HH:MM'}), HTTPStatus.BAD_REQUEST
        
        # Validate day_of_week if provided
        if 'day_of_week' in data and not 1 <= data['day_of_week'] <= 7:
            return jsonify({'error': 'day_of_week must be between 1 and 7'}), HTTPStatus.BAD_REQUEST
            
        updateable_fields = ['section_type', 'section_code', 'day_of_week', 
                           'start_time', 'end_time', 'capacity', 'term', 
                           'academic_year']
        
        for field in updateable_fields:
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
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<int:offering_id>/enrollment', methods=['PATCH'], strict_slashes=False)
def update_enrollment(offering_id):
    try:
        offering = CourseOffering.query.get_or_404(offering_id)
        data = request.get_json()
        
        if 'current_enrollment' not in data:
            return jsonify({'error': 'current_enrollment is required'}), HTTPStatus.BAD_REQUEST
            
        if not isinstance(data['current_enrollment'], int) or data['current_enrollment'] < 0:
            return jsonify({'error': 'Invalid enrollment count'}), HTTPStatus.BAD_REQUEST
            
        # Update enrollment and status
        offering.current_enrollment = data['current_enrollment']
        
        # Auto-update status based on enrollment
        if offering.current_enrollment >= offering.capacity:
            offering.status = 'FULL'
        elif offering.current_enrollment == 0:
            offering.status = 'OPEN'
            
        db.session.commit()
        
        return jsonify({
            'offering_id': offering.offering_id,
            'current_enrollment': offering.current_enrollment,
            'capacity': offering.capacity,
            'status': offering.status
        }), HTTPStatus.OK
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<int:offering_id>/status', methods=['PATCH'], strict_slashes=False)
def update_status(offering_id):
    try:
        offering = CourseOffering.query.get_or_404(offering_id)
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({'error': 'status is required'}), HTTPStatus.BAD_REQUEST
            
        valid_statuses = ['OPEN', 'FULL', 'CANCELLED']
        if data['status'] not in valid_statuses:
            return jsonify({
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), HTTPStatus.BAD_REQUEST
            
        offering.status = data['status']
        db.session.commit()
        
        return jsonify({
            'offering_id': offering.offering_id,
            'status': offering.status
        }), HTTPStatus.OK
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<int:offering_id>', methods=['DELETE'], strict_slashes=False)
def delete_offering(offering_id):
    try:
        offering = CourseOffering.query.get_or_404(offering_id)
        
        # Delete associated block schedules first
        BlockSchedule.query.filter_by(offering_id=offering_id).delete()
        
        # Prevent deletion if offering has enrollments
        if offering.current_enrollment > 0:
            return jsonify({
                'error': 'Cannot delete offering with active enrollments'
            }), HTTPStatus.CONFLICT

        # Delete the offering
        db.session.delete(offering)
        db.session.commit()
        
        return '', HTTPStatus.NO_CONTENT
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

    

@bp.route('/bulk', methods=['POST'])
def create_offerings_bulk():
    try:
        data = request.get_json()
        if not data or 'offerings' not in data:
            return jsonify({'error': 'No offerings provided'}), HTTPStatus.BAD_REQUEST
            
        offerings_data = data['offerings']
        created_offerings = []
        errors = []
        
        for offering_data in offerings_data:
            # Check required fields
            required_fields = [
                'course_id', 'section_type', 'section_code', 
                'day_of_week', 'start_time', 'end_time', 
                'capacity', 'term', 'academic_year'
            ]
            
            if not all(k in offering_data for k in required_fields):
                errors.append(f"Missing required fields for offering {offering_data.get('course_id', 'Unknown')}")
                continue

            # Validate term
            if offering_data['term'] not in ['FALL', 'WINTER']:
                errors.append(f"Invalid term for offering {offering_data['course_id']}")
                continue

            # Validate academic year format (YYYY-YYYY)
            if not re.match(r'^\d{4}-\d{4}$', offering_data['academic_year']):
                errors.append(f"Invalid academic year format for offering {offering_data['course_id']}")
                continue
                
            # Check if course exists, if not create it
            course = Course.query.get(offering_data['course_id'])
            if not course:
                course = Course(
                    course_id=offering_data['course_id'],
                    course_name=offering_data.get('course_name', f'{offering_data["course_id"]}'),
                    credits=offering_data.get('credits', 0.5)
                )
                db.session.add(course)
                
            # Validate section_type
            valid_types = ['LECTURE', 'LAB', 'TUTORIAL']
            if offering_data['section_type'] not in valid_types:
                errors.append(f"Invalid section_type for offering {offering_data['course_id']}")
                continue
                
            # Validate times
            try:
                start_time = datetime.strptime(offering_data['start_time'], '%H:%M').time()
                end_time = datetime.strptime(offering_data['end_time'], '%H:%M').time()
                if end_time <= start_time:
                    errors.append(f"End time must be after start time for offering {offering_data['course_id']}")
                    continue
            except ValueError:
                errors.append(f"Invalid time format for offering {offering_data['course_id']}")
                continue

            # Check for duplicate section in same term/year
            existing = CourseOffering.query.filter_by(
                course_id=offering_data['course_id'],
                section_code=offering_data['section_code'],
                term=offering_data['term'],
                academic_year=offering_data['academic_year']
            ).first()
            
            if existing:
                errors.append(f"Section already exists for {offering_data['course_id']} in {offering_data['term']} {offering_data['academic_year']}")
                continue
                
            # Create offering
            offering = CourseOffering(
                course_id=offering_data['course_id'],
                section_type=offering_data['section_type'],
                section_code=offering_data['section_code'],
                day_of_week=int(offering_data['day_of_week']),
                start_time=start_time,
                end_time=end_time,
                capacity=int(offering_data['capacity']),
                term=offering_data['term'],
                academic_year=offering_data['academic_year'],
                status='OPEN',
                current_enrollment=0
            )
            db.session.add(offering)
            created_offerings.append({
                'course_id': offering_data['course_id'],
                'section_code': offering_data['section_code'],
                'term': offering_data['term'],
                'academic_year': offering_data['academic_year']
            })
            
        if errors and not created_offerings:
            db.session.rollback()
            return jsonify({
                'error': 'Validation failed',
                'errors': errors
            }), HTTPStatus.BAD_REQUEST
            
        db.session.commit()
        return jsonify({
            'message': f'{len(created_offerings)} offerings created successfully',
            'created': created_offerings,
            'errors': errors
        }), HTTPStatus.CREATED
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR
