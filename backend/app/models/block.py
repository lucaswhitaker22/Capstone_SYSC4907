# app/models/block.py
from app import db

class Block(db.Model):
    __tablename__ = 'block'

    block_id = db.Column(db.String(20), primary_key=True)
    program_id = db.Column(db.String(10), db.ForeignKey('program.program_id'), nullable=False)
    block_size = db.Column(db.Integer, nullable=False)
    term = db.Column(db.String(10), nullable=False)
    academic_year = db.Column(db.String(9), nullable=False)
    schedule_rating = db.Column(db.Numeric(5,2))
    early_starts = db.Column(db.Integer)
    late_ends = db.Column(db.Integer)
    long_breaks = db.Column(db.Integer)
    consecutive_days = db.Column(db.Integer)
    status = db.Column(db.String(20), default='DRAFT')

    # Relationships
    block_schedules = db.relationship('BlockSchedule', backref='block', lazy=True)

    __table_args__ = (
        db.CheckConstraint('block_size IN (10, 20)', name='check_block_size'),
        db.UniqueConstraint('program_id', 'block_id', 'term', 'academic_year', 
                          name='unique_block'),
    )

    def __repr__(self):
        return f'<Block {self.block_id}>'