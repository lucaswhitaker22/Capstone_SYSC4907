# app/routes/courses.py
from flask import Blueprint, jsonify, request
from app.models import Course,CourseOffering
from app import db
from http import HTTPStatus

bp = Blueprint('courses', __name__, url_prefix='/api/courses')

@bp.route('/', methods=['GET'], strict_slashes=False)
def get_courses():
    # Add term filter for offerings
    term = request.args.get('term')
    academic_year = request.args.get('academic_year')
    
    courses = Course.query.all()
    response = []
    
    for c in courses:
        course_data = {
            'course_id': c.course_id,
            'course_name': c.course_name,
            'credits': float(c.credits)
        }
        
        # Add offering counts if term is specified
        if term and academic_year:
            offerings = CourseOffering.query.filter_by(
                course_id=c.course_id,
                term=term,
                academic_year=academic_year
            ).count()
            course_data['offerings_count'] = offerings
            
        response.append(course_data)
    
    return jsonify(response), HTTPStatus.OK

@bp.route('/bulk', methods=['POST'], strict_slashes=False)
def create_courses_bulk():
    try:
        data = request.get_json()
        if not data or 'courses' not in data:
            return jsonify({
                'error': 'No courses provided'
            }), HTTPStatus.BAD_REQUEST

        courses_data = data['courses']
        created_courses = []
        errors = []

        # Validate all courses before creating any
        for course_data in courses_data:
            # Check required fields
            if not all(k in course_data for k in ['course_id', 'course_name', 'credits']):
                errors.append(f"Missing required fields for course {course_data.get('course_id', 'Unknown')}")
                continue

            # Validate course_id format and existence
            if Course.query.get(course_data['course_id']):
                errors.append(f"Course {course_data['course_id']} already exists")
                continue

            # Validate credits
            try:
                credits = float(course_data['credits'])
                if credits <= 0:
                    errors.append(f"Credits must be positive for course {course_data['course_id']}")
                    continue
            except ValueError:
                errors.append(f"Invalid credits value for course {course_data['course_id']}")
                continue

        # If there are validation errors, return them
        if errors and not created_courses:
            return jsonify({
                'error': 'Validation failed',
                'errors': errors
            }), HTTPStatus.BAD_REQUEST

        # Create validated courses
        for course_data in courses_data:
            if course_data['course_id'] not in [e.split()[1] for e in errors]:
                course = Course(
                    course_id=course_data['course_id'],
                    course_name=course_data['course_name'],
                    credits=float(course_data['credits'])
                )
                db.session.add(course)
                created_courses.append(course_data['course_id'])

        db.session.commit()

        return jsonify({
            'message': 'Courses created successfully',
            'created': created_courses,
            'errors': errors
        }), HTTPStatus.CREATED if created_courses else HTTPStatus.BAD_REQUEST

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR


@bp.route('/<course_id>', methods=['GET'], strict_slashes=False)
def get_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Get term-specific offering counts
    fall_offerings = CourseOffering.query.filter_by(
        course_id=course_id,
        term='FALL',
        academic_year='2025-2026'
    ).count()
    
    winter_offerings = CourseOffering.query.filter_by(
        course_id=course_id,
        term='WINTER',
        academic_year='2025-2026'
    ).count()
    
    return jsonify({
        'course_id': course.course_id,
        'course_name': course.course_name,
        'credits': float(course.credits),
        'fall_offerings_count': fall_offerings,
        'winter_offerings_count': winter_offerings
    }), HTTPStatus.OK

@bp.route('/', methods=['POST'], strict_slashes=False)
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

@bp.route('/<course_id>', methods=['PUT'], strict_slashes=False)
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

@bp.route('/<course_id>', methods=['DELETE'], strict_slashes=False)
def delete_course(course_id):
    try:
        course = Course.query.get_or_404(course_id)
        
        # Check if there are any associated offerings
        offerings = CourseOffering.query.filter_by(course_id=course_id).all()
        if offerings:
            return jsonify({
                'error': 'Cannot delete course with existing offerings'
            }), HTTPStatus.CONFLICT
        
        # Delete the course
        db.session.delete(course)
        db.session.commit()
        return '', HTTPStatus.NO_CONTENT
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

