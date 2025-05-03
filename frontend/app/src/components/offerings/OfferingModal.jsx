import React, { useEffect, useState } from 'react';
import { Modal, Form, Button, Row, Col, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { InfoCircle } from 'react-bootstrap-icons';

const OfferingModal = ({ show, offering, onHide, onSave }) => {
  const initialFormData = {
    course_id: '',
    section_type: 'LECTURE',
    section_code: '',
    day_of_week: '1',
    start_time: '',
    end_time: '',
    capacity: '',
    term: '',
    academic_year: '',
    status: 'OPEN'
  };

  const [formData, setFormData] = useState(initialFormData);
  const [validated, setValidated] = useState(false);
  const [courses, setCourses] = useState([]);

  // Fetch courses for dropdown
  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/api/courses/');
        const data = await response.json();
        setCourses(data);
      } catch (error) {
        console.error('Error fetching courses:', error);
      }
    };
    fetchCourses();
  }, []);

  useEffect(() => {
    if (offering) {
      setFormData({
        course_id: offering.course_id,
        section_type: offering.section_type,
        section_code: offering.section_code,
        day_of_week: offering.day_of_week.toString(),
        start_time: offering.start_time,
        end_time: offering.end_time,
        capacity: offering.capacity,
        term: offering.term,
        academic_year: offering.academic_year,
        status: offering.status
      });
    } else {
      setFormData(initialFormData);
    }
    setValidated(false);
  }, [offering, show]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    if (form.checkValidity()) {
      onSave({
        ...formData,
        day_of_week: parseInt(formData.day_of_week),
        capacity: parseInt(formData.capacity)
      });
    }
    setValidated(true);
  };

  // Helper function to create tooltips
  const renderTooltip = (text) => (
    <OverlayTrigger
      placement="right"
      overlay={<Tooltip>{text}</Tooltip>}
    >
      <InfoCircle className="ms-2" />
    </OverlayTrigger>
  );

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>{offering ? 'Edit Course Offering' : 'Add Course Offering'}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form noValidate validated={validated} onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>
              Course
              {renderTooltip("Select the course for which you're creating an offering")}
            </Form.Label>
            <Form.Select 
              name="course_id" 
              value={formData.course_id} 
              onChange={handleChange}
              required
            >
              <option value="">Select a course...</option>
              {courses.map(course => (
                <option key={course.course_id} value={course.course_id}>
                  {course.course_id} - {course.course_name}
                </option>
              ))}
            </Form.Select>
            <Form.Control.Feedback type="invalid">
              Please select a course.
            </Form.Control.Feedback>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>
              Section Type
              {renderTooltip("Specify whether this is a lecture, lab, or tutorial component")}
            </Form.Label>
            <Form.Select 
              name="section_type" 
              value={formData.section_type} 
              onChange={handleChange}
              required
            >
              <option value="LECTURE">Lecture</option>
              <option value="LAB">Lab</option>
              <option value="TUTORIAL">Tutorial</option>
            </Form.Select>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>
              Section Code
              {renderTooltip("A unique letter (A-F) to identify different sections of the same course")}
            </Form.Label>
            <Form.Select 
              name="section_code" 
              value={formData.section_code} 
              onChange={handleChange}
              required
            >
              <option value="">Select a section code...</option>
              {['A', 'B', 'C', 'D', 'E', 'F'].map(code => (
                <option key={code} value={code}>
                  {code}
                </option>
              ))}
            </Form.Select>
            <Form.Control.Feedback type="invalid">
              Please select a section code.
            </Form.Control.Feedback>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>
              Day
              {renderTooltip("The day of the week when this section meets")}
            </Form.Label>
            <Form.Select 
              name="day_of_week" 
              value={formData.day_of_week} 
              onChange={handleChange}
              required
            >
              <option value="1">Monday</option>
              <option value="2">Tuesday</option>
              <option value="3">Wednesday</option>
              <option value="4">Thursday</option>
              <option value="5">Friday</option>
            </Form.Select>
          </Form.Group>

          <Row>
            <Col>
              <Form.Group className="mb-3">
                <Form.Label>
                  Start Time (HH:MM)
                  {renderTooltip("Enter the start time in 24-hour format (e.g., 14:30 for 2:30 PM)")}
                </Form.Label>
                <Form.Control
                  type="text"
                  name="start_time"
                  value={formData.start_time}
                  onChange={handleChange}
                  placeholder="HH:MM"
                  pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
                  required
                />
                <Form.Control.Feedback type="invalid">
                  Please provide a valid start time.
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
            <Col>
              <Form.Group className="mb-3">
                <Form.Label>
                  End Time (HH:MM)
                  {renderTooltip("Enter the end time in 24-hour format (e.g., 16:00 for 4:00 PM)")}
                </Form.Label>
                <Form.Control
                  type="text"
                  name="end_time"
                  value={formData.end_time}
                  onChange={handleChange}
                  placeholder="HH:MM"
                  pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
                  required
                />
                <Form.Control.Feedback type="invalid">
                  Please provide a valid end time.
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
          </Row>

          <Form.Group className="mb-3">
            <Form.Label>
              Capacity
              {renderTooltip("Maximum number of students that can enroll in this section")}
            </Form.Label>
            <Form.Control
              type="number"
              name="capacity"
              value={formData.capacity}
              onChange={handleChange}
              min="1"
              required
            />
            <Form.Control.Feedback type="invalid">
              Please provide a valid capacity.
            </Form.Control.Feedback>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>
              Term
              {renderTooltip("The academic term when this course is offered")}
            </Form.Label>
            <Form.Select 
              name="term" 
              value={formData.term} 
              onChange={handleChange}
              required
            >
              <option value="">Select a term</option>
              <option value="Fall">Fall</option>
              <option value="Winter">Winter</option>
            </Form.Select>
            <Form.Control.Feedback type="invalid">
              Please select a term.
            </Form.Control.Feedback>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>
              Academic Year
              {renderTooltip("Enter in YYYY-YYYY format (e.g., 2025-2026)")}
            </Form.Label>
            <Form.Control
              type="text"
              name="academic_year"
              value={formData.academic_year}
              onChange={handleChange}
              placeholder="YYYY-YYYY"
              pattern="^\d{4}-\d{4}$"
              required
            />
            <Form.Control.Feedback type="invalid">
              Please provide a valid academic year (YYYY-YYYY).
            </Form.Control.Feedback>
          </Form.Group>

          {offering && (
            <Form.Group className="mb-3">
              <Form.Label>
                Status
                {renderTooltip("Current enrollment status of this section")}
              </Form.Label>
              <Form.Select 
                name="status" 
                value={formData.status} 
                onChange={handleChange}
                required
              >
                <option value="OPEN">Open</option>
                <option value="FULL">Full</option>
                <option value="CANCELLED">Cancelled</option>
              </Form.Select>
            </Form.Group>
          )}

          <div className="d-flex justify-content-end gap-2">
            <Button variant="secondary" onClick={onHide}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Save
            </Button>
          </div>
        </Form>
      </Modal.Body>
    </Modal>
  );
};

export default OfferingModal;
