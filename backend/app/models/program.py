# app/models/program.py
from app import db

class Program(db.Model):
    __tablename__ = 'program'

    program_id = db.Column(db.String(10), primary_key=True)
    program_name = db.Column(db.String(100), nullable=False)
    total_enrollment = db.Column(db.Integer, nullable=False)
    blocks_20_count_fall = db.Column(db.Integer, nullable=False, default=0)  # New field
    blocks_10_count_fall = db.Column(db.Integer, nullable=False, default=0)  # New field
    blocks_20_count_winter = db.Column(db.Integer, nullable=False, default=0)  # New field
    blocks_10_count_winter = db.Column(db.Integer, nullable=False, default=0)  # New field

    # Relationships
    blocks = db.relationship('Block', backref='program', lazy=True)
    program_requirements = db.relationship('ProgramRequirement', backref='program', lazy=True)
    def __repr__(self):
        return f'<Program {self.program_id}>'