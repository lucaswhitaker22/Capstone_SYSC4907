from flask import Blueprint, jsonify, request, current_app
from app.models import BlockSchedule, Block, CourseOffering, ProgramRequirement
from app.database import db
from http import HTTPStatus
from app.routes.conflicts import has_time_conflict
import logging

def generate_block_schedule(block_id):
    try:
        # Get block and validate
        block = Block.query.get_or_404(block_id)
        if block.status == 'LOCKED':
            return jsonify({
                'error': 'Cannot modify locked block'
            }), HTTPStatus.FORBIDDEN

        # Get term-specific program requirements
        program_requirements = ProgramRequirement.query.filter_by(
    program_id=block.program_id
).order_by(ProgramRequirement.requirement_id).all()

        if not program_requirements:
            return jsonify({
                'error': f'No requirements found for program in {block.term} term'
            }), HTTPStatus.NOT_FOUND

        # Get required course IDs
        required_courses = [req.course_id for req in program_requirements]

        # Get all existing schedules to check for duplicates (within same term/year)
        existing_schedules = BlockSchedule.query.join(Block).filter(
            BlockSchedule.block_id != block_id,
            Block.term == block.term,
            Block.academic_year == block.academic_year
        ).all()

        # Group existing schedules by block for comparison
        existing_block_schedules = {}
        for schedule in existing_schedules:
            if schedule.block_id not in existing_block_schedules:
                existing_block_schedules[schedule.block_id] = []
            existing_block_schedules[schedule.block_id].append(schedule.offering_id)

        # Get all available offerings for required courses in the same term/year
        available_offerings = CourseOffering.query.filter(
            CourseOffering.course_id.in_(required_courses),
            CourseOffering.term == block.term,
            CourseOffering.academic_year == block.academic_year
        ).all()

        # Group offerings by course
        course_offerings = {}
        for offering in available_offerings:
            if offering.course_id not in course_offerings:
                course_offerings[offering.course_id] = {'LECTURE': [], 'LAB': [], 'TUTORIAL': []}
            course_offerings[offering.course_id][offering.section_type].append(offering)

        valid_schedules = []

        def try_schedule_combination(current_schedule, remaining_courses, course_offerings):
            if not remaining_courses:
                current_offering_ids = set(o.offering_id for o in current_schedule)
                for block_schedule in existing_block_schedules.values():
                    if set(block_schedule) == current_offering_ids:
                        return
                valid_schedules.append(current_schedule.copy())
                return

            current_course = remaining_courses[0]
            if current_course not in course_offerings:
                return

            # Group lectures by their section prefix
            lecture_groups = {}
            for lecture in course_offerings[current_course]['LECTURE']:
                prefix = lecture.section_code.split('-')[0]
                if prefix not in lecture_groups:
                    lecture_groups[prefix] = []
                lecture_groups[prefix].append(lecture)

            # Try each lecture group
            for prefix, lectures in lecture_groups.items():
                all_lectures_fit = True
                temp_schedule = current_schedule.copy()

                for lecture in lectures:
                    if any(has_time_conflict(lecture, selected) for selected in temp_schedule):
                        all_lectures_fit = False
                        break
                    temp_schedule.append(lecture)

                if all_lectures_fit:
                    if course_offerings[current_course]['LAB']:
                        for lab in course_offerings[current_course]['LAB']:
                            if not any(has_time_conflict(lab, selected) for selected in temp_schedule):
                                try_schedule_combination(
                                    temp_schedule + [lab],
                                    remaining_courses[1:],
                                    course_offerings
                                )
                    else:
                        try_schedule_combination(
                            temp_schedule,
                            remaining_courses[1:],
                            course_offerings
                        )

        # Generate all valid schedules
        try_schedule_combination([], required_courses, course_offerings)

        if not valid_schedules:
            return jsonify({
                'error': f'No valid schedule found for {block.term} term that satisfies all requirements'
            }), HTTPStatus.BAD_REQUEST

        # Select the first valid schedule
        selected_schedule = valid_schedules[0]

        # Clear existing schedule
        BlockSchedule.query.filter_by(block_id=block_id).delete()

        # Create block schedules for selected offerings
        for offering in selected_schedule:
            block_schedule = BlockSchedule(
                block_id=block_id,
                offering_id=offering.offering_id
            )
            db.session.add(block_schedule)

        # Calculate and set the rating
        rating_response = rate_block_schedule(block_id)
        if isinstance(rating_response, tuple):
            rating_data = rating_response[0].get_json()
            rating = rating_data.get('rating', 0)  # Extract just the numerical rating
        else:
            rating = rating_response.get('rating', 0)

        block.schedule_rating = rating 
        db.session.commit()

        formatted_offerings = [{
            'offering_id': o.offering_id,
            'course_id': o.course_id,
            'requirement_id': next(
                (r.requirement_id for r in program_requirements if r.course_id == o.course_id),
                None
            ),
            'section_type': o.section_type,
            'section_code': o.section_code,
            'day_of_week': o.day_of_week,
            'start_time': o.start_time.strftime('%H:%M'),
            'end_time': o.end_time.strftime('%H:%M'),
            'term': block.term,
            'academic_year': block.academic_year
        } for o in selected_schedule]

        return jsonify({
            'block_id': block_id,
            'term': block.term,
            'academic_year': block.academic_year,
            'schedule': formatted_offerings,
            'scheduled_courses': required_courses,
            'total_valid_schedules': len(valid_schedules),
            'schedule_rating': rating
        }), HTTPStatus.CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR


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
