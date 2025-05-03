import React from 'react';
import { Container, Accordion, Card, Alert, Table } from 'react-bootstrap';


const HelpPage = () => {
  return (
    <Container className="py-4">
      <h1 className="mb-4">Help & Documentation</h1>

      <Alert variant="info" className="mb-4">
        <Alert.Heading>Course Management System</Alert.Heading>
        <p>
          This web application is intended to assist administrators to generate course scehdules for first year engieering students at Carleton University.
          Also includes utilities for managing for course information/offerings, blocks, conflicts, schedules, requirements, and program data for academic planning.
        </p>
      </Alert>

      <Accordion defaultActiveKey="0" className="mb-4">

        <Accordion.Item eventKey="0">
          <Accordion.Header>Getting Started</Accordion.Header>
          <Accordion.Body>
            <p>The Course Management System helps you manage various aspects of academic planning:</p>
            <ul>
              <li><strong>Courses</strong> - Manage course information and basic details</li>
              <li><strong>Course Offerings</strong> - Handle course sections, schedules, and enrollment capacities</li>
              <li><strong>Programs</strong> - Manage programs, requirements, and student allocations</li>
              <li><strong>Blocks</strong> - Manage blocks and their schedules</li>
              <li><strong>Conflicts</strong> - Detect conflicts between courses/schedules</li>
              <li><strong>Schedule</strong> - View and manage block schedules</li>
            </ul>
            <Accordion defaultActiveKey="0" className="mb-4">
              <Accordion.Item eventKey="1">
                <Accordion.Header>Course Offerings</Accordion.Header>
                <Accordion.Body>
                  <h5>Managing Course Offerings</h5>
                  <p>Course offerings represent specific sections of courses for a term:</p>
                  <ul>
                    <li>Create offerings for lectures, labs, and tutorials</li>
                    <li>Set schedule details (day, time)</li>
                    <li>Set capacity and enrollment information</li>
                    <li>Specify term and academic year</li>
                    <li>Import/export offerings via CSV</li>
                  </ul>
                </Accordion.Body>
              </Accordion.Item>

              <Accordion.Item eventKey="2">
                <Accordion.Header>Programs</Accordion.Header>
                <Accordion.Body>
                  <h5>Program Management</h5>
                  <p>The Programs section allows you to:</p>
                  <ul>
                    <li>Create and manage academic programs</li>
                    <li>Set enrollment numbers</li>
                    <li>Configure block distribution</li>
                    <li>Define program requirements</li>
                  </ul>
                </Accordion.Body>
              </Accordion.Item>

              <Accordion.Item eventKey="5">
                <Accordion.Header>Conflicts</Accordion.Header>
                <Accordion.Body>
                  <h5>Conflict Detection</h5>
                  <p>The system provides three types of conflict checks:</p>
                  <ul>
                    <li><strong>Offering Conflicts</strong> - Check time conflicts between two specific offerings</li>
                    <li><strong>Schedule Conflicts</strong> - Check conflicts in a set of offerings</li>
                    <li><strong>Course Conflicts</strong> - Check if a new course conflicts with existing schedule</li>
                  </ul>
                </Accordion.Body>
              </Accordion.Item>

              <Accordion.Item eventKey="6">
                <Accordion.Header>Schedule</Accordion.Header>
                <Accordion.Body>
                  <h5>Block Scheduling</h5>
                  <p>The Schedule section allows you to:</p>
                  <ul>
                    <li>View block schedules for Fall and Winter terms</li>
                    <li>Manually edit block schedules</li>
                    <li>Generate optimized schedules automatically</li>
                    <li>Validate schedules against program requirements</li>
                    <li>Perform bulk operations on multiple blocks</li>
                  </ul>
                </Accordion.Body>
              </Accordion.Item>
            </Accordion>
          </Accordion.Body>
        </Accordion.Item>
        <Accordion>

          <Accordion.Item eventKey="0">
            <Accordion.Header>Schedule Generation (Step-by-Step Guide)</Accordion.Header>
            <Accordion.Body>
              <h5>Complete Workflow for Schedule Generation</h5>
              <p>Follow these steps to set up and generate schedules for your academic blocks:</p>



              <div className="border-start border-4 border-success ps-3 mb-4">
                <h6 className="fw-bold">Step 1: Create Course Offerings</h6>
                <ol>
                  <li>Navigate to the <strong>Course Offerings</strong> page</li>
                  <li>Click <strong>Add Offering</strong> and select a course</li>
                  <li>For each offering, specify:
                    <ul>
                      <li>Section Type (LECTURE, LAB, or TUTORIAL)</li>
                      <li>Section Code (A, B, C, etc.)</li>
                      <li>Day of Week</li>
                      <li>Start and End Times</li>
                      <li>Capacity</li>
                      <li>Term (FALL or WINTER)</li>
                      <li>Academic Year</li>
                    </ul>
                  </li>
                  <li>Click <strong>Save</strong> to create the offering</li>
                  <li>Alternatively, use the <strong>Import</strong> feature to upload multiple offerings via CSV</li>
                  <li>Verify all offerings appear correctly in the table</li>
                </ol>
              </div>

              <div className="border-start border-4 border-warning ps-3 mb-4">
                <h6 className="fw-bold">Step 2: Set Up Programs</h6>
                <ol>
                  <li>Navigate to the <strong>Programs</strong> page</li>
                  <li>Click <strong>Add Program</strong> and provide:
                    <ul>
                      <li>Program ID (e.g., CS-HONOURS)</li>
                      <li>Program Name (e.g., Computer Science Honours)</li>
                      <li>Academic Year</li>
                      <li>Number of students</li>
                    </ul>
                  </li>
                  <li>Click <strong>Save</strong> to create the program</li>
                  <li>For each program, click <strong>Manage Requirements</strong></li>
                  <li>Add required courses for the program:
                    <ul>
                      <li>Select courses from the dropdown</li>
                      <li>Specify the term (FALL or WINTER)</li>
                      <li>Click <strong>Add Requirement</strong></li>
                    </ul>
                  </li>
                  <li>Verify all program requirements are correctly listed</li>
                </ol>
              </div>

              <div className="border-start border-4 border-info ps-3 mb-4">
                <h6 className="fw-bold">Step 3: Generate and Manage Schedules</h6>
                <ol>
                  <li>Navigate to the <strong>Schedule</strong> page</li>
                  <li>Select the Academic Year and Term (FALL or WINTER)</li>
                  <li>For individual block scheduling:
                    <ul>
                      <li>Locate the block you want to schedule</li>
                      <li>Click the <strong>Generate</strong> button</li>
                      <li>The system will create an optimized schedule based on program requirements</li>
                      <li>Review the generated schedule and its rating</li>
                    </ul>
                  </li>
                  <li>For bulk scheduling:
                    <ul>
                      <li>Select multiple blocks using the checkboxes</li>
                      <li>Click <strong>Bulk Generate</strong></li>
                      <li>Wait for all schedules to be created</li>
                    </ul>
                  </li>
                  <li>To view a schedule, click the <strong>View</strong> button</li>
                  <li>To modify a schedule, click the <strong>Edit</strong> button</li>
                  <li>To check if a schedule meets program requirements, click <strong>Validate</strong></li>
                  <li>If validation fails, add missing course offerings manually</li>
                  <li>Once satisfied, you can export schedules for distribution</li>
                </ol>
              </div>

              <div className="border-start border-4 border-secondary ps-3 mb-4">
                <h6 className="fw-bold">Step 4 (Optional): Check for Conflicts</h6>
                <ol>
                  <li>Navigate to the <strong>Conflicts</strong> page</li>
                  <li>Use the conflict detection tools:
                    <ul>
                      <li><strong>Offering Conflicts</strong>: Check if two specific offerings conflict</li>
                      <li><strong>Schedule Conflicts</strong>: Check for conflicts within a set of offerings</li>
                      <li><strong>Course Conflicts</strong>: Check if a course conflicts with existing schedules</li>
                    </ul>
                  </li>
                  <li>Resolve any conflicts by adjusting schedules or offerings</li>
                  <li>Re-validate schedules after resolving conflicts</li>
                </ol>
              </div>

              <div className="alert alert-secondary">
                <h6 className="fw-bold">Tips for Successful Schedule Generation</h6>
                <ul>
                  <li><strong>Complete Prerequisites</strong>: Ensure all courses, offerings, programs, and blocks are created before attempting to generate schedules</li>
                  <li><strong>Offering Variety</strong>: Create multiple offerings for each course to give the scheduler more options</li>
                  <li><strong>Check Requirements</strong>: Verify that all program requirements have corresponding course offerings in the correct term</li>
                  <li><strong>Balanced Distribution</strong>: Create offerings across different days and times to avoid scheduling bottlenecks</li>
                  <li><strong>Iterative Approach</strong>: If generation produces poor results, try regenerating several times</li>
                  <li><strong>Manual Adjustments</strong>: Use the edit feature to fine-tune automatically generated schedules</li>
                  <li><strong>Conflict Resolution</strong>: Always check for and resolve conflicts before finalizing schedules</li>
                  <li><strong>Validation</strong>: Validate all schedules to ensure they meet program requirements</li>
                  <li><strong>Backup</strong>: Export and save your schedules regularly</li>
                  <li><strong>Block Size</strong>: Consider using smaller blocks (10 students) for programs with many requirements</li>
                  <li><strong>Time Distribution</strong>: Aim for schedules that distribute classes evenly throughout the week</li>
                  <li><strong>Capacity Management</strong>: Ensure course offerings have sufficient capacity for all blocks assigned to them</li>
                  <li><strong>Term Balance</strong>: Try to balance course load between Fall and Winter terms</li>
                  <li><strong>Priority Courses</strong>: Schedule difficult-to-place courses first when doing manual adjustments</li>
                  <li><strong>Regular Updates</strong>: Update course offerings if sections are canceled or full</li>
                </ul>
              </div>
            </Accordion.Body>
          </Accordion.Item>


        </Accordion>


      </Accordion>
      <Card className="mb-4">
        <Card.Header as="h5">Frequently Asked Questions</Card.Header>
        <Card.Body>
          <Accordion>
            <Accordion.Item eventKey="0">
              <Accordion.Header>How does the schedule generation algorithm work?</Accordion.Header>
              <Accordion.Body>
                The schedule generation algorithm works through these steps:
                <ol>
                  <li>Retrieves the block's program requirements to determine which courses need to be scheduled</li>
                  <li>Finds available course offerings with sufficient capacity for the block size</li>
                  <li>Checks existing schedules to avoid creating duplicate schedules</li>
                  <li>Groups offerings by course and section type (LECTURE, LAB, TUTORIAL)</li>
                  <li>Uses a recursive approach to try different combinations of offerings</li>
                  <li>Ensures no time conflicts exist between selected offerings</li>
                  <li>Randomizes course selection order to generate varied schedules</li>
                  <li>When multiple valid schedules are found, randomly selects one</li>
                  <li>Updates course enrollments based on the block size</li>
                  <li>Calculates a rating for the generated schedule</li>
                </ol>
                <p>The algorithm prioritizes creating conflict-free schedules that include all required courses while ensuring sufficient capacity for the block size.</p>
              </Accordion.Body>
            </Accordion.Item>

            <Accordion.Item eventKey="1">
              <Accordion.Header>How does the schedule rating algorithm work? What do the different rating criteria mean?</Accordion.Header>
              <Accordion.Body>
                <p>The schedule rating algorithm evaluates schedules on a 100-point scale based on three main criteria:</p>

                <h6 className="fw-bold">1. Time Distribution (40 points)</h6>
                <p>Measures how evenly classes are distributed across different times of day:</p>
                <ul>
                  <li>Morning: Classes before 12:00</li>
                  <li>Afternoon: Classes between 12:00-17:00</li>
                  <li>Evening: Classes after 17:00</li>
                </ul>
                <p>A higher score means classes are more evenly distributed across these time slots.</p>

                <h6 className="fw-bold">2. Day Distribution (30 points)</h6>
                <p>Evaluates how well classes are spread across the week:</p>
                <ul>
                  <li>Maximum score (30 points) if classes use all 5 weekdays</li>
                  <li>Proportionally lower scores for fewer days (e.g., 18 points for using 3 days)</li>
                </ul>
                <p>Schedules that spread classes across more days of the week score higher.</p>

                <h6 className="fw-bold">3. Gap Analysis (30 points)</h6>
                <p>Penalizes schedules with long gaps between classes on the same day:</p>
                <ul>
                  <li>Gaps longer than 3 hours receive penalties</li>
                  <li>More penalties result in a lower score</li>
                </ul>
                <p>Schedules with fewer long gaps between classes score higher.</p>

                <p>A total rating of 80 or above is considered excellent, while ratings below 60 may indicate scheduling issues that could be improved.</p>
              </Accordion.Body>
            </Accordion.Item>

            <Accordion.Item eventKey="2">
              <Accordion.Header>What does the validation check do? How does it check if a schedule is valid?</Accordion.Header>
              <Accordion.Body>
                <p>The validation check ensures that a block's schedule meets all program requirements. It performs these checks:</p>

                <ol>
                  <li><strong>Course Coverage:</strong> Verifies that all required courses for the program are scheduled in the block</li>
                  <li><strong>Lecture Section Groups:</strong> Checks that all sections within a lecture group (e.g., A-1, A-2) are included when required</li>
                  <li><strong>Lab Requirements:</strong> Ensures that lab sections are scheduled for courses that require them</li>
                </ol>

                <p>The validation process:</p>
                <ol>
                  <li>Retrieves the block and its scheduled offerings</li>
                  <li>Groups offerings by course ID and section type</li>
                  <li>Compares against program requirements</li>
                  <li>Identifies any missing requirements</li>
                  <li>Returns a validation result with details about any missing requirements</li>
                </ol>

                <p>A schedule is considered valid only when it includes all required courses with their appropriate section types (lectures, labs, tutorials) for the specific term and academic year.</p>

                <p>If validation fails, the system provides specific information about which requirements are missing, allowing you to manually add them to complete the schedule.</p>
              </Accordion.Body>
            </Accordion.Item>

          </Accordion>
        </Card.Body>
      </Card>





      <Card className="mb-4">
        <Card.Header as="h5">Credit & Contact</Card.Header>
        <Card.Body>
          <ul>
            <li><strong>Name:</strong> Lucas Whitaker (101195445)</li>
            <li><strong>Email:</strong> lucaswhitaker@cmail.carleton.ca</li>
          </ul>
        </Card.Body>
      </Card>
    </Container>



  );
};

export default HelpPage;
