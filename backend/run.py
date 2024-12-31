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
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    with app.app_context():
        try:
            # Clear existing data
            models_to_clear = [
                BlockSchedule, Block, CourseOffering, 
                ProgramRequirement, Course, Program
            ]
            for model in models_to_clear:
                model.query.delete()
            
            # Define data files mapping
            data_files = {
                (Program, 'programs.csv'): {
                    'program_id': str,
                    'program_name': str,
                    'total_enrollment': int,
                    'blocks_20_count': int,
                    'blocks_10_count': int
                },
                (Course, 'courses.csv'): {
                    'course_id': str,
                    'course_name': str,
                    'credits': float
                },
                (CourseOffering, 'course_offerings.csv'): {
                    'offering_id': int,
                    'course_id': str,
                    'section_type': str,
                    'section_code': str,
                    'day_of_week': int,
                    'start_time': parse_time,
                    'end_time': parse_time,
                    'capacity': int,
                    'current_enrollment': int,
                    'term': str,
                    'academic_year': str,
                    'status': str
                }
            }

            # Seed data using the mapping
            for (model, filename), field_types in data_files.items():
                file_path = os.path.join(base_dir, 'sample_data', filename)
                with open(file_path, 'r') as file:
                    for row in csv.DictReader(file):
                        processed_data = {
                            field: converter(row[field]) 
                            for field, converter in field_types.items()
                        }
                        db.session.add(model(**processed_data))

            # Seed program requirements
            with open(os.path.join(base_dir, 'sample_data', 'program_requirements.csv'), 'r') as file:
                for row in csv.DictReader(file):
                    if row['course_id'] != 'ElectiveB':
                        db.session.add(ProgramRequirement(**row))

            # Seed blocks and schedules
            for filename, model in [('blocks.csv', Block), ('block_schedules.csv', BlockSchedule)]:
                with open(os.path.join(base_dir, 'sample_data', filename), 'r') as file:
                    for row in csv.DictReader(file):
                        db.session.add(model(**row))

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