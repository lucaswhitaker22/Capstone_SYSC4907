from flask import jsonify, current_app
from app.models import BlockSchedule, Block, CourseOffering
from http import HTTPStatus

def rate_block_schedule(block_id):
    try:
        block = Block.query.get_or_404(block_id)
        
        # Get block schedules for specific term/year
        block_schedules = BlockSchedule.query.join(CourseOffering).filter(
            BlockSchedule.block_id == block_id
        ).all()
        
        if not block_schedules:
            return jsonify({
                'rating': 0,
                'term': block.term,
                'academic_year': block.academic_year
            }), HTTPStatus.OK
            
        # Filter offerings by term and academic year
        offerings = [
            schedule.course_offering for schedule in block_schedules 
            if schedule.course_offering.term == block.term 
            and schedule.course_offering.academic_year == block.academic_year
        ]
        
        if not offerings:
            return jsonify({
                'rating': 0,
                'term': block.term,
                'academic_year': block.academic_year,
                'error': 'No offerings found for specified term and year'
            }), HTTPStatus.OK
            
        total_points = 0
        
        # Criterion 1: Time Distribution (40 points)
        time_slots = {
            'morning': 0,    # Before 12:00
            'afternoon': 0,  # 12:00-17:00
            'evening': 0     # After 17:00
        }
        
        for offering in offerings:
            hour = offering.start_time.hour
            if hour < 12:
                time_slots['morning'] += 1
            elif hour < 17:
                time_slots['afternoon'] += 1
            else:
                time_slots['evening'] += 1
                
        if len(offerings) > 0:
            distribution_score = 40 * (1 - (max(time_slots.values()) - min(time_slots.values())) / len(offerings))
            total_points += distribution_score
        
        # Criterion 2: Day Distribution (30 points)
        days_used = len(set(o.day_of_week for o in offerings))
        day_distribution_score = 30 * (days_used / 5)  # Assuming 5 weekdays
        total_points += day_distribution_score
        
        # Criterion 3: Gap Analysis (30 points)
        daily_schedules = {}
        for offering in offerings:
            if offering.day_of_week not in daily_schedules:
                daily_schedules[offering.day_of_week] = []
            daily_schedules[offering.day_of_week].append(offering)

        gap_penalties = 0
        for day_schedule in daily_schedules.values():
            sorted_offerings = sorted(day_schedule, key=lambda x: x.start_time)
            for i in range(len(sorted_offerings) - 1):
                # Convert times to datetime for proper subtraction
                from datetime import datetime, timedelta
                current_date = datetime.now().date()
                end_time = datetime.combine(current_date, sorted_offerings[i].end_time)
                start_time = datetime.combine(current_date, sorted_offerings[i+1].start_time)
                gap = (start_time - end_time).total_seconds() / 3600
                if gap > 3:  # Penalize gaps longer than 3 hours
                    gap_penalties += 1
                        
            gap_score = 30 * (1 - (gap_penalties / len(offerings)))
            total_points += gap_score
        
        return jsonify({
            'block_id': block_id,
            'term': block.term,
            'academic_year': block.academic_year,
            'rating': round(total_points, 1),
            'time_distribution': {
                'morning': time_slots['morning'],
                'afternoon': time_slots['afternoon'],
                'evening': time_slots['evening']
            },
            'days_used': days_used,
            'gap_penalties': gap_penalties
        }), HTTPStatus.OK
        
    except Exception as e:
        current_app.logger.error(f"Error rating schedule for block {block_id}: {str(e)}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'block_id': block_id
        }), HTTPStatus.INTERNAL_SERVER_ERROR
