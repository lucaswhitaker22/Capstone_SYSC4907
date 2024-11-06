# System Overview
The project aims to develop a software system that automatically generates and ranks course schedules for first-year students across 13 Bachelor of Engineering (BEng) programs. The system will use the course schedule provided by the university and take into account various constraints and rules to ensure that the generated schedules are practical, conflict-free, and meet student needs.

## Project Objectives

1. Develop a web-based course scheduling system for BEng programs
2. Generate conflict-free schedules automatically
3. Implement a basic ranking system for schedule optimization
4. Provide an intuitive interface for administrators and students

## Functional Requirements

1. Data Management:
   - The system shall parse course data from CSV files
   - The system shall store course information in an SQLite database
   - The system shall validate course data for completeness and correctness

2. Schedule Generation:
   - The system shall generate conflict-free schedules for a given set of courses
   - The system shall respect room and lab capacity limits when assigning courses
   - The system shall consider prerequisite requirements when generating schedules

3. Schedule Ranking:
   - The system shall rank generated schedules based on predefined criteria
   - The system shall sort schedules from most to least desirable

4. User Interface:
   - The system shall provide an administrator view for generating and managing schedules
   - The system shall provide a student view for accessing assigned schedules
   - The system shall display schedules in a weekly grid format

5. Export Functionality:
   - The system shall allow users to export schedules as PDF files
   - The system shall provide a print-friendly version of schedules

## Non-Functional Requirements

1. Performance:
   - The system shall generate schedules for up to 500 students within 5 minutes
   - The system shall support concurrent access by at least 50 users

2. Usability:
   - The user interface shall be responsive and compatible with major web browsers
   - The system shall provide clear error messages for invalid inputs or conflicts

3. Reliability:
   - The system shall maintain data integrity during schedule generation and updates
   - The system shall have an uptime of at least 99% during peak usage periods

4. Security:
   - The system shall implement user authentication for accessing administrator and student views
   - The system shall encrypt sensitive data stored in the database

5. Maintainability:
   - The system's codebase shall be well-documented with inline comments
   - The system shall use modular design to facilitate future updates and extensions

6. Scalability:
   - The system shall be designed to accommodate future expansion to multiple programs
   - The database schema shall support the addition of new course types and constraints
