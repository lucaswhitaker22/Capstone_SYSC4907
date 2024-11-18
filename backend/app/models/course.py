# app/models/course.py
from app import db

class Course(db.Model):
    __tablename__ = 'course'

    course_id = db.Column(db.String(10), primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Numeric(2,1), nullable=False)

    # Relationships
    offerings = db.relationship('CourseOffering', backref='course', lazy=True)
    program_requirements = db.relationship('ProgramRequirement', backref='course', lazy=True)

    def __repr__(self):
        return f'<Course {self.course_id}>'