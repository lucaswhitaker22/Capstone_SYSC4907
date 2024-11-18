# app/models/course_offering.py
from app import db

class CourseOffering(db.Model):
    __tablename__ = 'course_offering'

    offering_id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(10), db.ForeignKey('course.course_id'), nullable=False)
    section_type = db.Column(db.String(20), nullable=False)
    section_code = db.Column(db.String(5), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    current_enrollment = db.Column(db.Integer, default=0)
    term = db.Column(db.String(10), nullable=False)
    academic_year = db.Column(db.String(9), nullable=False)
    status = db.Column(db.String(20), default='OPEN')

    # Relationships
    block_schedules = db.relationship('BlockSchedule', backref='course_offering', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('course_id', 'section_type', 'section_code', 
                          'term', 'academic_year', name='unique_section'),
    )

    def __repr__(self):
        return f'<CourseOffering {self.course_id} {self.section_code}>'