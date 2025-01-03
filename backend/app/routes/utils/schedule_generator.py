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

        # Get program requirements
        program_requirements = ProgramRequirement.query.filter_by(
            program_id=block.program_id
        ).order_by(ProgramRequirement.requirement_id).all()

        if not program_requirements:
            return jsonify({
                'error': 'No requirements found for program'
            }), HTTPStatus.NOT_FOUND

        # Get required course IDs
        required_courses = [req.course_id for req in program_requirements]

        # Get all existing schedules to check for duplicates
        existing_schedules = BlockSchedule.query.filter(
            BlockSchedule.block_id != block_id
        ).all()

        # Group existing schedules by block for comparison
        existing_block_schedules = {}
        for schedule in existing_schedules:
            if schedule.block_id not in existing_block_schedules:
                existing_block_schedules[schedule.block_id] = []
            existing_block_schedules[schedule.block_id].append(schedule.offering_id)

        # Get all available offerings for required courses
        available_offerings = CourseOffering.query.filter(
            CourseOffering.course_id.in_(required_courses)
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
                # Check if this schedule is identical to any existing block schedule
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

                # Add all lectures from this section group
                for lecture in lectures:
                    if any(has_time_conflict(lecture, selected) for selected in temp_schedule):
                        all_lectures_fit = False
                        break
                    temp_schedule.append(lecture)

                if all_lectures_fit:
                    if course_offerings[current_course]['LAB']:
                        # Try each lab with this lecture group
                        for lab in course_offerings[current_course]['LAB']:
                            if not any(has_time_conflict(lab, selected) for selected in temp_schedule):
                                try_schedule_combination(
                                    temp_schedule + [lab],
                                    remaining_courses[1:],
                                    course_offerings
                                )
                    else:
                        # No lab required, continue with next course
                        try_schedule_combination(
                            temp_schedule,
                            remaining_courses[1:],
                            course_offerings
                        )

        # Generate all valid schedules
        try_schedule_combination([], required_courses, course_offerings)

        if not valid_schedules:
            return jsonify({
                'error': 'No valid schedule found that satisfies all requirements'
            }), HTTPStatus.BAD_REQUEST

        # Select the first valid schedule (you could implement a selection strategy here)
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

        db.session.commit()

        # Format response
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
            'end_time': o.end_time.strftime('%H:%M')
        } for o in selected_schedule]

        return jsonify({
            'schedule': formatted_offerings,
            'scheduled_courses': required_courses,
            'total_valid_schedules': len(valid_schedules)
        }), HTTPStatus.CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR
