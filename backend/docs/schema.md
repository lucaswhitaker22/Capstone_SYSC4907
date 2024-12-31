## Database Schema Documentation

The backend uses SQLAlchemy ORM to define the following database schema:

### Course

Represents academic courses.

- `course_id` (String, Primary Key): Unique identifier for the course
- `course_name` (String): Name of the course
- `credits` (Numeric): Number of credits for the course

### Program

Represents academic programs.

- `program_id` (String, Primary Key): Unique identifier for the program
- `program_name` (String): Name of the program
- `total_enrollment` (Integer): Total number of students enrolled in the program
- `blocks_20_count` (Integer): Number of 20-student blocks in the program
- `blocks_10_count` (Integer): Number of 10-student blocks in the program

### CourseOffering

Represents specific offerings of courses.

- `offering_id` (Integer, Primary Key): Unique identifier for the offering
- `course_id` (String, Foreign Key): Reference to the Course
- `section_type` (String): Type of section (e.g., LECTURE, LAB, TUTORIAL)
- `section_code` (String): Code for the section
- `day_of_week` (Integer): Day of the week for the offering
- `start_time` (Time): Start time of the offering
- `end_time` (Time): End time of the offering
- `capacity` (Integer): Maximum capacity of the offering
- `current_enrollment` (Integer): Current number of enrolled students
- `term` (String): Term of the offering (e.g., FALL, WINTER)
- `academic_year` (String): Academic year of the offering
- `status` (String): Status of the offering (e.g., OPEN, FULL, CANCELLED)

### ProgramRequirement

Represents course requirements for programs.

- `program_id` (String, Foreign Key, Primary Key): Reference to the Program
- `course_id` (String, Foreign Key, Primary Key): Reference to the Course
- `term` (String, Primary Key): Term in which the course is required

### Block

Represents blocks of courses.

- `block_id` (String, Primary Key): Unique identifier for the block
- `program_id` (String, Foreign Key): Reference to the Program
- `block_size` (Integer): Size of the block (10 or 20)
- `term` (String): Term of the block
- `academic_year` (String): Academic year of the block
- `schedule_rating` (Numeric): Rating of the block's schedule
- `early_starts` (Integer): Number of early start times in the block
- `late_ends` (Integer): Number of late end times in the block
- `long_breaks` (Integer): Number of long breaks in the block
- `consecutive_days` (Integer): Number of consecutive days in the block
- `status` (String): Status of the block (e.g., DRAFT, PUBLISHED, LOCKED)

### BlockSchedule

Represents the schedule of courses within a block.

- `block_id` (String, Foreign Key, Primary Key): Reference to the Block
- `offering_id` (Integer, Foreign Key, Primary Key): Reference to the CourseOffering

## Relationships

- Course has many CourseOfferings (one-to-many)
- Program has many Blocks (one-to-many)
- Program has many ProgramRequirements (one-to-many)
- Course has many ProgramRequirements (one-to-many)
- Block has many BlockSchedules (one-to-many)
- CourseOffering has many BlockSchedules (one-to-many)

## Constraints

- Block size is constrained to be either 10 or 20
- Unique constraint on (program_id, block_id, term, academic_year) for Block
- Unique constraint on (course_id, section_type, section_code, term, academic_year) for CourseOffering

This schema provides a comprehensive structure for managing academic programs, courses, course offerings, and block schedules, allowing for efficient querying and management of the academic scheduling system[1].
