from flask import Blueprint, jsonify, request, current_app
from app.models import BlockSchedule, Block, CourseOffering, ProgramRequirement, Program
from app.database import db
from http import HTTPStatus
import logging

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
    

