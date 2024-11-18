# app/routes/__init__.py
from .courses import bp as courses_bp
from .programs import bp as programs_bp
from .course_offerings import bp as offerings_bp
from .blocks import bp as blocks_bp
from .program_requirements import bp as requirements_bp
from .block_schedules import bp as schedules_bp

__all__ = [
    'courses_bp',
    'programs_bp',
    'offerings_bp',
    'blocks_bp',
    'requirements_bp',
    'schedules_bp'
]