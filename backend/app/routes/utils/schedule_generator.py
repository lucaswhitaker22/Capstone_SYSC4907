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

        # Get program requirements with requirement_id
        program_requirements = ProgramRequirement.query.filter_by(
            program_id=block.program_id
        ).order_by(ProgramRequirement.requirement_id).all()

        if not program_requirements:
            return jsonify({
                'error': 'No requirements found for program'
            }), HTTPStatus.NOT_FOUND

        # Get required course IDs
        required_courses = [req.course_id for req in program_requirements]

        # Clear existing schedule
        BlockSchedule.query.filter_by(block_id=block_id).delete()
        db.session.commit()

        # Get available offerings for required courses that aren't already scheduled
        existing_schedules = BlockSchedule.query.filter(
            BlockSchedule.block_id != block_id
        ).all()
        used_offering_ids = {schedule.offering_id for schedule in existing_schedules}

        available_offerings = CourseOffering.query.filter(
            CourseOffering.course_id.in_(required_courses),
            ~CourseOffering.offering_id.in_(used_offering_ids)
        ).all()

        # Group offerings by course and section type
        course_offerings = {}
        for offering in available_offerings:
            if offering.course_id not in course_offerings:
                course_offerings[offering.course_id] = {'LECTURE': [], 'LAB': [], 'TUTORIAL': []}
            course_offerings[offering.course_id][offering.section_type].append(offering)

        selected_offerings = []
        scheduled_courses = set()
        failed_courses = []

        # Process requirements in order of requirement_id
        for requirement in program_requirements:
            course_id = requirement.course_id
            if course_id not in course_offerings:
                failed_courses.append(course_id)
                continue

            # Get lecture sections grouped by section code prefix
            lecture_groups = {}
            for lecture in course_offerings[course_id]['LECTURE']:
                section_prefix = lecture.section_code.split('-')[0]
                if section_prefix not in lecture_groups:
                    lecture_groups[section_prefix] = []
                lecture_groups[section_prefix].append(lecture)

            # Try each lecture group until we find one that works
            schedule_found = False
            for section_prefix, lectures in lecture_groups.items():
                if schedule_found:
                    break

                lectures_fit = True
                for lecture in lectures:
                    if any(has_time_conflict(lecture, selected) for selected in selected_offerings):
                        lectures_fit = False
                        break

                if lectures_fit:
                    compatible_lab = None
                    if course_offerings[course_id]['LAB']:
                        for lab in course_offerings[course_id]['LAB']:
                            lab_conflicts = any(has_time_conflict(lab, selected) 
                                             for selected in selected_offerings + lectures)
                            if not lab_conflicts:
                                compatible_lab = lab
                                break
                        
                        if not compatible_lab:
                            continue

                    # Add lectures and lab if required
                    selected_offerings.extend(lectures)
                    if compatible_lab:
                        selected_offerings.append(compatible_lab)
                    scheduled_courses.add(course_id)
                    schedule_found = True

            if not schedule_found:
                failed_courses.append(course_id)

        # Create block schedules for selected offerings
        for offering in selected_offerings:
            block_schedule = BlockSchedule(
                block_id=block_id,
                offering_id=offering.offering_id
            )
            db.session.add(block_schedule)

        db.session.commit()

        # Return formatted offerings with requirement information
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
        } for o in selected_offerings]

        response = {
            'schedule': formatted_offerings,
            'scheduled_courses': list(scheduled_courses)
        }

        if failed_courses:
            response['failed_courses'] = failed_courses
            response['warning'] = 'Some courses could not be scheduled'

        return jsonify(response), HTTPStatus.CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR
