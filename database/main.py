import sqlite3
import csv
import os

DB_NAME = 'course_scheduler.db'

CSV_FILES = {
    'Course': './sample_data/courses.csv',
    'Program': './sample_data/programs.csv',
    'CourseOffering': './sample_data/course_offerings.csv',
    'ProgramRequirement': './sample_data/program_requirements.csv',
    'Block': './sample_data/blocks.csv',
    'BlockSchedule': './sample_data/block_schedules.csv'
}

CREATE_TABLES = {
    'Course': '''
    CREATE TABLE Course (
        course_id VARCHAR(10) PRIMARY KEY,
        course_name VARCHAR(100) NOT NULL,
        credits DECIMAL(2,1) NOT NULL
    )
    ''',
    'Program': '''
    CREATE TABLE Program (
        program_id VARCHAR(10) PRIMARY KEY,
        program_name VARCHAR(100) NOT NULL,
        total_enrollment INTEGER NOT NULL,
        blocks_20_count INTEGER NOT NULL,
        blocks_10_count INTEGER NOT NULL
    )
    ''',
    'CourseOffering': '''
        CREATE TABLE CourseOffering (
            offering_id INTEGER PRIMARY KEY,
            course_id VARCHAR(10) REFERENCES Course(course_id),
            section_type VARCHAR(20) NOT NULL,
            section_code VARCHAR(5) NOT NULL,
            day_of_week INTEGER NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            capacity INTEGER NOT NULL,
            current_enrollment INTEGER DEFAULT 0,
            term VARCHAR(10) NOT NULL,
            academic_year VARCHAR(9) NOT NULL,
            status VARCHAR(20) DEFAULT 'OPEN',  -- OPEN, FULL
            UNIQUE(course_id, section_type, section_code, term, academic_year)
        )
    ''',
    'ProgramRequirement': '''
    CREATE TABLE ProgramRequirement (
        program_id VARCHAR(10) REFERENCES Program(program_id),
        course_id VARCHAR(10) REFERENCES Course(course_id),
        term VARCHAR(10) NOT NULL,          -- FALL, WINTER
        PRIMARY KEY (program_id, course_id, term)
    )
    ''',
    'Block': '''
        CREATE TABLE Block (
            block_id VARCHAR(20) PRIMARY KEY,
            program_id VARCHAR(10) REFERENCES Program(program_id),
            block_size INTEGER NOT NULL CHECK (block_size IN (10, 20)),
            term VARCHAR(10) NOT NULL,
            academic_year VARCHAR(9) NOT NULL,
            schedule_rating DECIMAL(5,2),
            early_starts INTEGER,           -- Count of 8:30 starts
            late_ends INTEGER,             -- Count of after 18:00 ends
            long_breaks INTEGER,           -- Count of >3 hour breaks
            consecutive_days INTEGER,      -- Count of consecutive full days
            status VARCHAR(20) DEFAULT 'DRAFT',  -- DRAFT, PUBLISHED, LOCKED
            UNIQUE(program_id, block_id, term, academic_year)
        )
    ''',
    'BlockSchedule': '''
    CREATE TABLE BlockSchedule (
        block_id VARCHAR(20) REFERENCES Block(block_id),
        offering_id INTEGER REFERENCES CourseOffering(offering_id),
        PRIMARY KEY (block_id, offering_id)
    )
    '''
}

def create_database():
    """Create the SQLite database and tables."""
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for table_name, create_statement in CREATE_TABLES.items():
        cursor.execute(create_statement)
        print(f"Created table: {table_name}")

    conn.commit()
    conn.close()

def import_csv_data():
    """Import data from CSV files into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for table, file_path in CSV_FILES.items():
        with open(file_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip header row
            data = [tuple(row) for row in csv_reader]
            
            placeholders = ','.join(['?' for _ in range(len(data[0]))])
            insert_query = f"INSERT INTO {table.capitalize()} VALUES ({placeholders})"
            
            cursor.executemany(insert_query, data)
            print(f"Imported data into table: {table.capitalize()}")

    conn.commit()
    conn.close()

def verify_imports():
    """Verify the data imports by counting rows in each table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for table in CSV_FILES.keys():
        cursor.execute(f"SELECT COUNT(*) FROM {table.capitalize()}")
        count = cursor.fetchone()[0]
        print(f"{table.capitalize()}: {count} rows")

    conn.close()

if __name__ == "__main__":
    create_database()
    import_csv_data()
    verify_imports()
    print("Database initialized and sample data imported successfully.")