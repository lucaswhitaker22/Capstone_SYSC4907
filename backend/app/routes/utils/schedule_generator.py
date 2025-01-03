from flask import Blueprint, jsonify, request, current_app
from app.models import BlockSchedule, Block, CourseOffering, ProgramRequirement, Program
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

        # Get available offerings excluding ones already used in other blocks
        existing_schedules = BlockSchedule.query.filter(
            BlockSchedule.block_id != block_id
        ).all()
        used_offering_ids = {schedule.offering_id for schedule in existing_schedules}

        available_offerings = CourseOffering.query.filter(
            CourseOffering.course_id.in_(required_courses),
            ~CourseOffering.offering_id.in_(used_offering_ids)
        ).all()

        # Group offerings by course
        course_offerings = {}
        for offering in available_offerings:
            if offering.course_id not in course_offerings:
                course_offerings[offering.course_id] = {'LECTURE': [], 'LAB': [], 'TUTORIAL': []}
            course_offerings[offering.course_id][offering.section_type].append(offering)

        def try_schedule_combination(current_schedule, remaining_courses, course_offerings):
            if not remaining_courses:
                return current_schedule

            current_course = remaining_courses[0]
            if current_course not in course_offerings:
                return None

            # Group lectures by their section prefix
            lecture_groups = {}
            for lecture in course_offerings[current_course]['LECTURE']:
                prefix = lecture.section_code.split('-')[0]
                if prefix not in lecture_groups:
                    lecture_groups[prefix] = []
                lecture_groups[prefix].append(lecture)

            # Try each lecture group (all sections with same prefix)
            for prefix, lectures in lecture_groups.items():
                # Must include ALL lectures in the group (A-1, A-2, etc.)
                all_lectures_fit = True
                temp_schedule = current_schedule.copy()

                # Add all lectures from this section group
                for lecture in lectures:
                    if any(has_time_conflict(lecture, selected) for selected in temp_schedule):
                        all_lectures_fit = False
                        break
                    temp_schedule.append(lecture)

                if all_lectures_fit:
                    # If course has labs, try each lab
                    if course_offerings[current_course]['LAB']:
                        lab_found = False
                        for lab in course_offerings[current_course]['LAB']:
                            if not any(has_time_conflict(lab, selected) for selected in temp_schedule):
                                # Try next course with all lectures and this lab
                                result = try_schedule_combination(
                                    temp_schedule + [lab],
                                    remaining_courses[1:],
                                    course_offerings
                                )
                                if result:
                                    return result
                                lab_found = True
                                break
                        if not lab_found:
                            continue
                    else:
                        # No lab required, try next course with all lectures
                        result = try_schedule_combination(
                            temp_schedule,
                            remaining_courses[1:],
                            course_offerings
                        )
                        if result:
                            return result

            return None


        # Try to find a valid schedule
        valid_schedule = try_schedule_combination([], required_courses, course_offerings)

        if not valid_schedule:
            return jsonify({
                'error': 'No valid schedule found that satisfies all requirements'
            }), HTTPStatus.BAD_REQUEST

        # Clear existing schedule
        BlockSchedule.query.filter_by(block_id=block_id).delete()

        # Create block schedules for selected offerings
        for offering in valid_schedule:
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
        } for o in valid_schedule]

        return jsonify({
            'schedule': formatted_offerings,
            'scheduled_courses': required_courses
        }), HTTPStatus.CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR
    


def validate_block_schedule(block_id):
    try:
        # Get block and its schedules
        block = Block.query.get_or_404(block_id)
        block_schedules = BlockSchedule.query.filter_by(block_id=block_id).all()
        
        if not block_schedules:
            return jsonify({
                'is_valid': False,
                'error': 'No schedule found for block'
            }), HTTPStatus.NOT_FOUND

        # Get all offerings in the block
        offerings = [schedule.course_offering for schedule in block_schedules]
        
        # Group offerings by course and section type
        course_schedules = {}
        for offering in offerings:
            if offering.course_id not in course_schedules:
                course_schedules[offering.course_id] = {
                    'LECTURE': {},
                    'LAB': [],
                    'TUTORIAL': []
                }
            if offering.section_type == 'LECTURE':
                prefix = offering.section_code.split('-')[0]
                if prefix not in course_schedules[offering.course_id]['LECTURE']:
                    course_schedules[offering.course_id]['LECTURE'][prefix] = []
                course_schedules[offering.course_id]['LECTURE'][prefix].append(offering)
            else:
                course_schedules[offering.course_id][offering.section_type].append(offering)

        # Get program requirements
        requirements = ProgramRequirement.query.filter_by(
            program_id=block.program_id
        ).all()

        missing_requirements = []
        for req in requirements:
            course_id = req.course_id
            
            # Check if course is scheduled
            if course_id not in course_schedules:
                missing_requirements.append({
                    'course_id': course_id,
                    'error': 'Course not scheduled'
                })
                continue

            # Get all available sections for this course
            available_sections = CourseOffering.query.filter_by(
                course_id=course_id
            ).all()

            # Group available lectures by prefix
            available_lecture_groups = {}
            for section in available_sections:
                if section.section_type == 'LECTURE':
                    prefix = section.section_code.split('-')[0]
                    if prefix not in available_lecture_groups:
                        available_lecture_groups[prefix] = []
                    available_lecture_groups[prefix].append(section.section_code)

            # Check if all sections of each lecture group are scheduled
            scheduled_lectures = course_schedules[course_id]['LECTURE']
            for prefix, sections in available_lecture_groups.items():
                if prefix in scheduled_lectures:
                    scheduled_sections = set(o.section_code for o in scheduled_lectures[prefix])
                    required_sections = set(sections)
                    if scheduled_sections != required_sections:
                        missing_requirements.append({
                            'course_id': course_id,
                            'error': f'Missing lecture sections for group {prefix}'
                        })

            # Check if lab is required and present
            has_labs = any(s.section_type == 'LAB' for s in available_sections)
            if has_labs and not course_schedules[course_id]['LAB']:
                missing_requirements.append({
                    'course_id': course_id,
                    'error': 'Missing lab section'
                })

        return jsonify({
            'block_id': block_id,
            'is_valid': len(missing_requirements) == 0,
            'missing_requirements': missing_requirements
        }), HTTPStatus.OK

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR
