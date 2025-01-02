# app/models/program_requirement.py
from app import db

class ProgramRequirement(db.Model):
    __tablename__ = 'program_requirement'

    program_id = db.Column(db.String(10), db.ForeignKey('program.program_id'), primary_key=True)
    course_id = db.Column(db.String(10), db.ForeignKey('course.course_id'), primary_key=True)

    def __repr__(self):
        return f'<ProgramRequirement {self.program_id} {self.course_id}>'