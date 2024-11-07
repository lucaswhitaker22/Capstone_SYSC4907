import sqlite3
import csv
import os

# Database file name
DB_NAME = 'course_scheduler.db'

# CSV file paths
CSV_FILES = {
    'course': './sample_data/courses.csv',
    'program': './sample_data/programs.csv',
    'programrequirement': './sample_data/program_requirements.csv',
    'room': './sample_data/rooms.csv',
    'section': './sample_data/sections.csv',
    'timeslot': './sample_data/timeslots.csv'
}

# SQL statements to create tables
CREATE_TABLES = {
    'Course': '''
    CREATE TABLE Course (
        course_id VARCHAR(10) PRIMARY KEY,
        course_name VARCHAR(100) NOT NULL,
        course_type VARCHAR(20) NOT NULL,
        department VARCHAR(20) NOT NULL,
        credits DECIMAL(2,1) NOT NULL,
        has_lab BOOLEAN DEFAULT false,
        has_tutorial BOOLEAN DEFAULT false
    )
    ''',
    'Program': '''
    CREATE TABLE Program (
        program_id VARCHAR(10) PRIMARY KEY,
        program_name VARCHAR(100) NOT NULL,
        department VARCHAR(50) NOT NULL,
        year INTEGER DEFAULT 1
    )
    ''',
    'ProgramRequirement': '''
    CREATE TABLE ProgramRequirement (
        program_id VARCHAR(10) REFERENCES Program(program_id),
        course_id VARCHAR(10) REFERENCES Course(course_id),
        term VARCHAR(10) NOT NULL,
        is_required BOOLEAN DEFAULT true,
        PRIMARY KEY (program_id, course_id, term)
    )
    ''',
    'Room': '''
    CREATE TABLE Room (
        room_id INTEGER PRIMARY KEY,
        building VARCHAR(50) NOT NULL,
        room_number VARCHAR(20) NOT NULL,
        capacity INTEGER NOT NULL,
        room_type VARCHAR(20) NOT NULL,
        UNIQUE(building, room_number)
    )
    ''',
    'Section': '''
    CREATE TABLE Section (
        section_id INTEGER PRIMARY KEY,
        course_id VARCHAR(10) REFERENCES Course(course_id),
        section_code VARCHAR(5) NOT NULL,
        type VARCHAR(20) NOT NULL,
        capacity INTEGER NOT NULL,
        room_id INTEGER REFERENCES Room(room_id),
        term VARCHAR(10) NOT NULL,
        academic_year VARCHAR(9) NOT NULL,
        parent_section_id INTEGER REFERENCES Section(section_id),
        UNIQUE(course_id, section_code, term, academic_year)
    )
    ''',
    'TimeSlot': '''
    CREATE TABLE TimeSlot (
        timeslot_id INTEGER PRIMARY KEY,
        section_id INTEGER REFERENCES Section(section_id),
        day_of_week INTEGER NOT NULL,
        start_time TIME NOT NULL,
        end_time TIME NOT NULL,
        UNIQUE(section_id, day_of_week, start_time)
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