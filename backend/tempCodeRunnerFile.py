# run.py
from app import create_app
from app.database import db
from app.models import Course, Program, CourseOffering, Block, BlockSchedule, ProgramRequirement
import csv
from datetime import datetime
import click
import os

app = create_app()

def parse_time(time_str):
    """Convert time string to datetime.time object"""
    return datetime.strptime(time_str, '%H:%M').time()

@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        print('Database initialized.')

@app.cli.command("seed-db")
def seed_db():
    """Seed the database with sample data."""
    # Ensure we're in the correct directory
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    with app.app_context():
        try:
            # Clear existing data
            BlockSchedule.query.delete()
            Block.query.delete()
            CourseOffering.query.delete()
            ProgramRequirement.query.delete()
            Course.query.delete()
            Program.query.delete()
            
            # Seed Programs
            programs_file = os.path.join(base_dir, 'sample_data', 'programs.csv')
            with open(programs_file, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    program = Program(
                        program_id=row['program_id'],
                        program_name=row['program_name'],
                        total_enrollment=int(row['total_enrollment']),
                        blocks_20_count=int(row['blocks_20_count']),
                        blocks_10_count=int(row['blocks_10_count'])
                    )
                    db.session.add(program)
            
            # Seed Courses
            courses_file = os.path.join(base_dir, 'sample_data', 'courses.csv')
            with open(courses_file, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    course = Course(
                        course_id=row['course_id'],
                        course_name=row['course_name'],
                        credits=float(row['credits'])
                    )
                    db.session.add(course)
            
            # Seed Course Offerings
            offerings_file = os.path.join(base_dir, 'sample_data', 'course_offerings.csv')
            with open(offerings_file, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    offering = CourseOffering(
                        offering_id=int(row['offering_id']),
                        course_id=row['course_id'],
                        section_type=row['section_type'],
                        section_code=row['section_code'],
                        day_of_week=int(row['day_of_week']),
                        start_time=parse_time(row['start_time']),
                        end_time=parse_time(row['end_time']),
                        capacity=int(row['capacity']),
                        current_enrollment=int(row['current_enrollment']),
                        term=row['term'],
                        academic_year=row['academic_year'],
                        status=row['status']
                    )
                    db.session.add(offering)
            
            # Seed Program Requirements
            requirements_file = os.path.join(base_dir, 'sample_data', 'program_requirements.csv')
            with open(requirements_file, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    if row['course_id'] != 'ElectiveB':  # Skip electives for now
                        requirement = ProgramRequirement(
                            program_id=row['program_id'],
                            course_id=row['course_id'],
                            term=row['term']
                        )
                        db.session.add(requirement)

            # Seed Blocks
            blocks_file = os.path.join(base_dir, 'sample_data', 'blocks.csv')
            with open(blocks_file, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    block = Block(
                        block_id=row['block_id'],
                        program_id=row['program_id'],
                        block_size=int(row['block_size']),
                        term=row['term'],
                        academic_year=row['academic_year'],
                        schedule_rating=float(row['schedule_rating']) if row['schedule_rating'] else None,
                        early_starts=int(row['early_starts']) if row['early_starts'] else 0,
                        late_ends=int(row['late_ends']) if row['late_ends'] else 0,
                        long_breaks=int(row['long_breaks']) if row['long_breaks'] else 0,
                        consecutive_days=int(row['consecutive_days']) if row['consecutive_days'] else 0,
                        status=row['status']
                    )
                    db.session.add(block)

            # Seed Block Schedules
            schedules_file = os.path.join(base_dir, 'sample_data', 'block_schedules.csv')
            with open(schedules_file, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    block_schedule = BlockSchedule(
                        block_id=row['block_id'],
                        offering_id=int(row['offering_id'])
                    )
                    db.session.add(block_schedule)
            
            # Commit all changes
            db.session.commit()
            print('Database seeded successfully.')
            
        except Exception as e:
            db.session.rollback()
            print(f'Error seeding database: {str(e)}')
            raise

@app.cli.command("clear-db")
def clear_db():
    """Clear all data from the database."""
    with app.app_context():
        try:
            BlockSchedule.query.delete()
            Block.query.delete()
            CourseOffering.query.delete()
            ProgramRequirement.query.delete()
            Course.query.delete()
            Program.query.delete()
            db.session.commit()
            print('Database cleared successfully.')
        except Exception as e:
            db.session.rollback()
            print(f'Error clearing database: {str(e)}')
            raise

if __name__ == '__main__':
    app.run(debug=True)