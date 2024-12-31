# app/routes/conflicts.py
from flask import Blueprint, jsonify, request
from app.models import CourseOffering, BlockSchedule
from http import HTTPStatus

bp = Blueprint('conflicts', __name__, url_prefix='/api/conflicts')

@bp.route('/offerings/<offering1_id>/<offering2_id>', methods=['GET'])
def check_offering_conflict(offering1_id, offering2_id):
    offering1 = CourseOffering.query.get_or_404(offering1_id)
    offering2 = CourseOffering.query.get_or_404(offering2_id)
    
    has_conflict = has_time_conflict(offering1, offering2)
    
    return jsonify({
        'has_conflict': has_conflict,
        'offering1': offering1.course_id,
        'offering2': offering2.course_id
    }), HTTPStatus.OK

@bp.route('/schedule/conflicts', methods=['POST'])
def check_schedule_conflicts():
    data = request.get_json()
    offering_ids = data.get('offering_ids', [])
    
    conflicts = _find_schedule_conflicts(offering_ids)
    
    return jsonify({
        'conflicts': conflicts
    }), HTTPStatus.OK

@bp.route('/schedule/check-course', methods=['POST'])
def check_course_conflicts():
    data = request.get_json()
    schedule_offering_ids = data.get('schedule_offering_ids', [])
    new_offering_id = data.get('new_offering_id')
    
    # Get the offerings
    schedule_offerings = CourseOffering.query.filter(
        CourseOffering.offering_id.in_(schedule_offering_ids)
    ).all()
    new_offering = CourseOffering.query.get_or_404(new_offering_id)
    
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
                'day_of_week': new_offering.day_of_week
            })
    
    return jsonify({'conflicts': conflicts}), HTTPStatus.OK

def has_time_conflict(offering1, offering2):
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

def _find_schedule_conflicts(offering_ids):
    offerings = [CourseOffering.query.get(id) for id in offering_ids]
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
                    'time1': f"{offering1.start_time}-{offering1.end_time}",
                    'time2': f"{offering2.start_time}-{offering2.end_time}"
                })
    
    return conflicts