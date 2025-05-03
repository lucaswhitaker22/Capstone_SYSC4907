from flask import Blueprint, jsonify, request, current_app
from app.models import BlockSchedule, Block, CourseOffering, ProgramRequirement
from app.database import db
from http import HTTPStatus
from app.routes.conflicts import has_time_conflict
from app.routes.utils.schedule_rating import rate_block_schedule
import logging
from flask import Blueprint, jsonify, request, current_app
from app.models import BlockSchedule, Block, CourseOffering, ProgramRequirement
from app.database import db
from http import HTTPStatus
from app.routes.conflicts import has_time_conflict
from app.routes.utils.schedule_rating import rate_block_schedule
import logging
import random  # Added for randomization

def generate_block_schedule(block_id):
    try:
        block = Block.query.get_or_404(block_id)
        if block.status == 'LOCKED':
            return jsonify({
                'error': 'Cannot modify locked block'
            }), HTTPStatus.FORBIDDEN

        program_requirements = ProgramRequirement.query.filter_by(
            program_id=block.program_id
        ).order_by(ProgramRequirement.requirement_id).all()

        if not program_requirements:
            return jsonify({
                'error': f'No requirements found for program'
            }), HTTPStatus.NOT_FOUND

        required_courses = [req.course_id for req in program_requirements]

        # Get existing schedules to check for duplicates
        existing_schedules = BlockSchedule.query.join(Block).filter(
            BlockSchedule.block_id != block_id,
            Block.term == block.term,
            Block.academic_year == block.academic_year
        ).all()

        existing_block_schedules = {}
        for schedule in existing_schedules:
            if schedule.block_id not in existing_block_schedules:
                existing_block_schedules[schedule.block_id] = []
            existing_block_schedules[schedule.block_id].append(schedule.offering_id)

        # Get offerings with sufficient capacity
        available_offerings = CourseOffering.query.filter(
            CourseOffering.course_id.in_(required_courses),
            CourseOffering.term == block.term,
            CourseOffering.academic_year == block.academic_year,
            CourseOffering.status != 'CANCELLED',
            CourseOffering.capacity - CourseOffering.current_enrollment >= block.block_size
        ).all()

        if not available_offerings:
            return jsonify({
                'error': f'No course offerings found with sufficient capacity for block size {block.block_size}'
            }), HTTPStatus.NOT_FOUND

        available_courses = set(offering.course_id for offering in available_offerings)
        courses_with_offerings = set(required_courses) & available_courses

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

            # Randomize course selection order
            course_idx = random.randrange(len(remaining_courses))
            current_course = remaining_courses.pop(course_idx)
            
            if current_course not in course_offerings:
                remaining_courses.append(current_course)  # Put it back for next iterations
                return

            lecture_groups = {}
            for lecture in course_offerings[current_course]['LECTURE']:
                if lecture.capacity - lecture.current_enrollment < block.block_size:
                    continue
                prefix = lecture.section_code.split('-')[0]
                if prefix not in lecture_groups:
                    lecture_groups[prefix] = []
                lecture_groups[prefix].append(lecture)

            # Randomize order of lecture group prefixes
            prefix_list = list(lecture_groups.keys())
            random.shuffle(prefix_list)

            for prefix in prefix_list:
                lectures = lecture_groups[prefix]
                all_lectures_fit = True
                temp_schedule = current_schedule.copy()

                for lecture in lectures:
                    if any(has_time_conflict(lecture, selected) for selected in temp_schedule):
                        all_lectures_fit = False
                        break
                    temp_schedule.append(lecture)

                if all_lectures_fit:
                    if course_offerings[current_course]['LAB']:
                        # Randomize the order of labs
                        labs = course_offerings[current_course]['LAB'].copy()
                        random.shuffle(labs)
                        
                        for lab in labs:
                            if lab.capacity - lab.current_enrollment < block.block_size:
                                continue
                            if not any(has_time_conflict(lab, selected) for selected in temp_schedule):
                                new_remaining = remaining_courses.copy()
                                try_schedule_combination(
                                    temp_schedule + [lab],
                                    new_remaining,
                                    course_offerings
                                )
                    else:
                        new_remaining = remaining_courses.copy()
                        try_schedule_combination(
                            temp_schedule,
                            new_remaining,
                            course_offerings
                        )
            
            # Put the course back for other branches of recursion
            remaining_courses.append(current_course)

        # Start with randomized course order
        course_list = list(courses_with_offerings)
        random.shuffle(course_list)
        try_schedule_combination([], course_list, course_offerings)

        if not valid_schedules:
            return jsonify({
                'error': f'Could not create valid schedule with available courses having sufficient capacity'
            }), HTTPStatus.BAD_REQUEST

        # Randomly select a schedule instead of always using the first one
        selected_schedule = random.choice(valid_schedules)

        # Reset enrollments for old schedule
        old_schedules = BlockSchedule.query.filter_by(block_id=block_id).all()
        for old_schedule in old_schedules:
            old_offering = CourseOffering.query.get(old_schedule.offering_id)
            old_offering.current_enrollment -= block.block_size
            if old_offering.current_enrollment < old_offering.capacity:
                old_offering.status = 'OPEN'
        BlockSchedule.query.filter_by(block_id=block_id).delete()

        # Create new schedule and update enrollments
        for offering in selected_schedule:
            block_schedule = BlockSchedule(
                block_id=block_id,
                offering_id=offering.offering_id
            )
            db.session.add(block_schedule)
            
            offering.current_enrollment += block.block_size
            if offering.current_enrollment >= offering.capacity:
                offering.status = 'FULL'

        rating_response = rate_block_schedule(block_id)
        rating_data = rating_response[0].get_json()
        rating = rating_data.get('rating', 0)

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
            'academic_year': block.academic_year,
            'current_enrollment': o.current_enrollment,
            'capacity': o.capacity,
            'status': o.status
        } for o in selected_schedule]

        return jsonify({
            'block_id': block_id,
            'term': block.term,
            'academic_year': block.academic_year,
            'schedule': formatted_offerings,
            'scheduled_courses': list(courses_with_offerings),
            'total_valid_schedules': len(valid_schedules),
            'schedule_rating': rating
        }), HTTPStatus.CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR
