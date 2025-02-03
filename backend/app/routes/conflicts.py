from flask import Blueprint, jsonify, request
from app.models import CourseOffering, BlockSchedule, Block
from http import HTTPStatus

bp = Blueprint('conflicts', __name__, url_prefix='/api/conflicts')

@bp.route('/offerings/<offering1_id>/<offering2_id>', methods=['GET'], strict_slashes=False)
def check_offering_conflict(offering1_id, offering2_id):
    offering1 = CourseOffering.query.get_or_404(offering1_id)
    offering2 = CourseOffering.query.get_or_404(offering2_id)
    
    # Check if offerings are in the same term and year
    if offering1.term != offering2.term or offering1.academic_year != offering2.academic_year:
        return jsonify({
            'has_conflict': False,
            'message': 'Offerings are in different terms/years',
            'offering1': {
                'course_id': offering1.course_id,
                'term': offering1.term,
                'academic_year': offering1.academic_year
            },
            'offering2': {
                'course_id': offering2.course_id,
                'term': offering2.term,
                'academic_year': offering2.academic_year
            }
        }), HTTPStatus.OK
    
    has_conflict = has_time_conflict(offering1, offering2)
    
    return jsonify({
        'has_conflict': has_conflict,
        'offering1': {
            'course_id': offering1.course_id,
            'term': offering1.term,
            'academic_year': offering1.academic_year
        },
        'offering2': {
            'course_id': offering2.course_id,
            'term': offering2.term,
            'academic_year': offering2.academic_year
        }
    }), HTTPStatus.OK

@bp.route('/schedule/conflicts', methods=['POST'], strict_slashes=False)
def check_schedule_conflicts():
    data = request.get_json()
    offering_ids = data.get('offering_ids', [])
    term = data.get('term')
    academic_year = data.get('academic_year')
    
    if not term or term not in ['FALL', 'WINTER']:
        return jsonify({'error': 'Invalid or missing term'}), HTTPStatus.BAD_REQUEST
        
    conflicts = _find_schedule_conflicts(offering_ids, term, academic_year)
    
    return jsonify({
        'term': term,
        'academic_year': academic_year,
        'conflicts': conflicts
    }), HTTPStatus.OK

@bp.route('/schedule/check-course', methods=['POST'], strict_slashes=False)
def check_course_conflicts():
    data = request.get_json()
    schedule_offering_ids = data.get('schedule_offering_ids', [])
    new_offering_id = data.get('new_offering_id')
    
    # Get the new offering first to check its term
    new_offering = CourseOffering.query.get_or_404(new_offering_id)
    
    # Get the offerings from the same term and year
    schedule_offerings = CourseOffering.query.filter(
        CourseOffering.offering_id.in_(schedule_offering_ids),
        CourseOffering.term == new_offering.term,
        CourseOffering.academic_year == new_offering.academic_year
    ).all()
    
    conflicts = []
    for existing_offering in schedule_offerings:
        if has_time_conflict(existing_offering, new_offering):
            conflicts.append({
                'existing_offering_id': existing_offering.offering_id,
                'existing_course_id': existing_offering.course_id,
                'existing_time': f"{existing_offering.start_time.strftime('%H:%M')}-{existing_offering.end_time.strftime('%H:%M')}",
                'new_offering_id': new_offering.offering_id,
                'new_course_id': new_offering.course_id,
                'new_time': f"{new_offering.start_time.strftime('%H:%M')}-{new_offering.end_time.strftime('%H:%M')}",
                'day_of_week': new_offering.day_of_week,
                'term': new_offering.term,
                'academic_year': new_offering.academic_year
            })
    
    return jsonify({
        'conflicts': conflicts,
        'term': new_offering.term,
        'academic_year': new_offering.academic_year
    }), HTTPStatus.OK

def has_time_conflict(offering1, offering2):
    # First check term and year match
    if offering1.term != offering2.term or offering1.academic_year != offering2.academic_year:
        return False
        
    # Only check conflicts on the same day
    if offering1.day_of_week != offering2.day_of_week:
        return False
    
    # Convert times to comparable format
    start1 = offering1.start_time
    end1 = offering1.end_time
    start2 = offering2.start_time
    end2 = offering2.end_time
    
    # Check for any overlap
    return (
        (start1 <= end2 and end1 >= start2) or  # offering1 overlaps with offering2
        (start2 <= end1 and end2 >= start1)      # offering2 overlaps with offering1
    )

def _find_schedule_conflicts(offering_ids, term, academic_year):
    # Get offerings only from specified term and year
    offerings = CourseOffering.query.filter(
        CourseOffering.offering_id.in_(offering_ids),
        CourseOffering.term == term,
        CourseOffering.academic_year == academic_year
    ).all()
    
    conflicts = []
    
    for i, offering1 in enumerate(offerings):
        for offering2 in offerings[i+1:]:
            if has_time_conflict(offering1, offering2):
                conflicts.append({
                    'offering1_id': offering1.offering_id,
                    'offering2_id': offering2.offering_id,
                    'course1_id': offering1.course_id,
                    'course2_id': offering2.course_id,
                    'day': offering1.day_of_week,
                    'time1': f"{offering1.start_time.strftime('%H:%M')}-{offering1.end_time.strftime('%H:%M')}",
                    'time2': f"{offering2.start_time.strftime('%H:%M')}-{offering2.end_time.strftime('%H:%M')}",
                    'term': term,
                    'academic_year': academic_year
                })
    
    return conflicts
