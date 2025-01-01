import React, { useEffect, useState } from 'react';
import { Modal, Form, Button, Row, Col } from 'react-bootstrap';

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

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>
          {offering ? 'Edit Course Offering' : 'Add Course Offering'}
        </Modal.Title>
      </Modal.Header>
      <Form noValidate validated={validated} onSubmit={handleSubmit}>
        <Modal.Body>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Course ID</Form.Label>
                <Form.Control
                  type="text"
                  name="course_id"
                  value={formData.course_id}
                  onChange={handleChange}
                  required
                  disabled={offering}
                />
                <Form.Control.Feedback type="invalid">
                  Please provide a course ID.
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Section Type</Form.Label>
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
            </Col>
          </Row>

          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Section Code</Form.Label>
                <Form.Control
                  type="text"
                  name="section_code"
                  value={formData.section_code}
                  onChange={handleChange}
                  required
                />
                <Form.Control.Feedback type="invalid">
                  Please provide a section code.
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Day</Form.Label>
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
            </Col>
          </Row>

          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Start Time (HH:MM)</Form.Label>
                <Form.Control
                  type="time"
                  name="start_time"
                  value={formData.start_time}
                  onChange={handleChange}
                  required
                />
                <Form.Control.Feedback type="invalid">
                  Please provide a valid start time.
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>End Time (HH:MM)</Form.Label>
                <Form.Control
                  type="time"
                  name="end_time"
                  value={formData.end_time}
                  onChange={handleChange}
                  required
                />
                <Form.Control.Feedback type="invalid">
                  Please provide a valid end time.
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
          </Row>

          <Row>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>Capacity</Form.Label>
                <Form.Control
                  type="number"
                  name="capacity"
                  value={formData.capacity}
                  onChange={handleChange}
                  required
                  min="1"
                />
                <Form.Control.Feedback type="invalid">
                  Please provide a valid capacity.
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>Term</Form.Label>
                <Form.Control
                  type="text"
                  name="term"
                  value={formData.term}
                  onChange={handleChange}
                  required
                />
                <Form.Control.Feedback type="invalid">
                  Please provide a term.
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>Academic Year</Form.Label>
                <Form.Control
                  type="text"
                  name="academic_year"
                  value={formData.academic_year}
                  onChange={handleChange}
                  required
                />
                <Form.Control.Feedback type="invalid">
                  Please provide an academic year.
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
          </Row>

          {offering && (
            <Row>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Status</Form.Label>
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
              </Col>
            </Row>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={onHide}>
            Cancel
          </Button>
          <Button variant="primary" type="submit">
            Save
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
};

export default OfferingModal;
