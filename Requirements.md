System Overview
The project aims to develop a software system that automatically generates and ranks course schedules for first-year students across 13 Bachelor of Engineering (BEng) programs. The system will use the course schedule provided by the university and take into account various constraints and rules to ensure that the generated schedules are practical, conflict-free, and meet student needs.

# Functional Requirements

Course Schedule Generation:
- The system must generate conflict-free schedules for all first-year students in one BEng program (focus on one program initially).
- The generated schedules must respect:
- Course prerequisites specific to each program.
- Room and lab capacity limits.

Schedule Ranking:
Implement a ranking mechanism based on predefined rules:
Avoid schedules that end late at night (20:30) and start early the next morning (08:30).
Minimize large gaps between classes on the same day (e.g., avoid a break from 11:30 to 16:00).
Rank schedules from most to least desirable based on these criteria.

Real-Time Updates:
Allow administrators to modify course schedules dynamically as enrollment changes during the summer.

Web Interface:
Develop a web-based interface using HTML, CSS, and JavaScript.
Create two views:
- Administrator View: For generating, modifying, and viewing schedules.
- Student View: For viewing assigned schedules.

Schedule Display and Export:
Display generated schedules in a weekly grid format.
Implement functionality to export schedules to PDF or print them directly from the browser.

Conflict Detection:
Ensure that no two courses in a student's schedule overlap in time.

Error Handling:
Implement input validation for data entry (e.g., correct format for CSV files).
Develop error reporting for scheduling conflicts or capacity issues.
