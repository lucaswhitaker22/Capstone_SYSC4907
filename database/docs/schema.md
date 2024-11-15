Here's the documentation for your course scheduling database schema:

## Core Tables

### Course
This table stores information about individual courses offered by the institution.
- **course_id**: Unique identifier for each course (e.g., ECOR1041)
- **course_name**: Full name of the course
- **course_type**: Categorizes courses as CORE, ELECTIVE_B, or ELECTIVE_C
- **department**: Department offering the course
- **credits**: Number of credits for the course

### Program
Stores information about academic programs and their block requirements.
- **program_id**: Unique identifier for each program (e.g., ARCH)
- **program_name**: Full name of the program
- **total_enrollment**: Total number of students in the program
- **blocks_20_count**: Number of 20-student blocks needed
- **blocks_10_count**: Number of 10-student blocks needed

### CourseOffering
Represents specific sections of courses with their scheduling details.
- **offering_id**: Unique identifier for each course offering
- **course_id**: Reference to the Course table
- **section_type**: Type of section (LECTURE, LAB, TUTORIAL)
- **section_code**: Specific code for the section (e.g., A1, B2)
- **day_of_week**: Day of the week (1-5 for Monday to Friday)
- **start_time**: Start time of the class
- **end_time**: End time of the class
- **capacity**: Maximum number of students
- **current_enrollment**: Current number of enrolled students
- **term**: Academic term (FALL, WINTER)
- **academic_year**: Academic year (e.g., 2024-2025)
- **status**: Section status (ACTIVE, CANCELLED, FULL)

### ProgramRequirement
Links courses to programs, specifying required courses for each term.
- **program_id**: Reference to the Program table
- **course_id**: Reference to the Course table
- **term**: Term when the course should be taken
- **sequence_order**: Order of prerequisites

### Block
Represents groups of students (10 or 20) with their schedule quality metrics.
- **block_id**: Unique identifier for each block
- **program_id**: Reference to the Program table
- **block_size**: Size of the block (10 or 20 students)
- **term**: Academic term
- **academic_year**: Academic year
- **schedule_rating**: Quality rating of the schedule
- **early_starts**: Count of 8:30 AM starts
- **late_ends**: Count of after 18:00 ends
- **long_breaks**: Count of breaks longer than 3 hours
- **consecutive_days**: Count of consecutive full days
- **status**: Block status (DRAFT, PUBLISHED, LOCKED)

### BlockSchedule
Links blocks to specific course offerings, forming complete schedules.
- **block_id**: Reference to the Block table
- **offering_id**: Reference to the CourseOffering table

### BlockEnrollment
Tracks enrollment numbers for each block.
- **block_id**: Reference to the Block table
- **current_enrollment**: Current number of students in the block
- **max_enrollment**: Maximum allowed enrollment
- **last_updated**: Timestamp of last update

## Key Features
1. **Block-Based Scheduling**
   - Supports both 20 and 10-student blocks
   - Tracks schedule quality metrics
   - Manages block status and enrollment

2. **Schedule Quality Assessment**
   - Tracks early morning starts
   - Monitors late evening ends
   - Counts long breaks between classes
   - Tracks consecutive full days

3. **Enrollment Management**
   - Tracks current enrollment in sections and blocks
   - Enforces capacity limits
   - Monitors enrollment status

4. **Program Requirements**
   - Manages course prerequisites
   - Specifies term-specific requirements
   - Supports different program structures

5. **Status Tracking**
   - Course offering status (ACTIVE, CANCELLED, FULL)
   - Block status (DRAFT, PUBLISHED, LOCKED)
   - Enrollment updates

This schema supports:
- Conflict-free schedule generation
- Block-based student grouping
- Schedule quality assessment
- Enrollment tracking
- Program-specific requirements
- Term-based course planning

Citations:
[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/28400840/b7a2baf4-0ff2-4c1c-b3c4-5bd771d3025d/paste.txt