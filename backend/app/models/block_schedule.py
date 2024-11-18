# app/models/block_schedule.py
from app import db

class BlockSchedule(db.Model):
    __tablename__ = 'block_schedule'

    block_id = db.Column(db.String(20), db.ForeignKey('block.block_id'), primary_key=True)
    offering_id = db.Column(db.Integer, db.ForeignKey('course_offering.offering_id'), primary_key=True)

    def __repr__(self):
        return f'<BlockSchedule {self.block_id} {self.offering_id}>'