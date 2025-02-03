# app/models/program_requirement.py
from app import db
from .enums import Term
class ProgramRequirement(db.Model):
    __tablename__ = 'program_requirement'
    
    requirement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    program_id = db.Column(db.String(10), db.ForeignKey('program.program_id'), nullable=False)
    course_id = db.Column(db.String(10), db.ForeignKey('course.course_id'), nullable=False)
    term = db.Column(db.Enum(Term), nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('program_id', 'course_id', 'term', name='unique_program_course_term'),
    )

    def __repr__(self):
        return f'<ProgramRequirement {self.program_id} {self.course_id}>'
