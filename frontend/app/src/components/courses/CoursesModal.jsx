import React, { useState, useEffect } from 'react';
import { Modal, Form, Button } from 'react-bootstrap';

const CourseModal = ({ show, onHide, course, onSave }) => {
  const initialFormData = {
    course_id: '',
    course_name: '',
    credits: ''
  };

  const [formData, setFormData] = useState(initialFormData);
  const [validated, setValidated] = useState(false);

  useEffect(() => {
    if (course) {
      setFormData({
        course_id: course.course_id,
        course_name: course.course_name,
        credits: course.credits.toString()
      });
    } else {
      setFormData(initialFormData);
    }
    setValidated(false);
  }, [course, show]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    
    if (form.checkValidity()) {
      try {
        const url = course 
          ? `http://127.0.0.1:5000/api/courses/${course.course_id}`
          : 'http://127.0.0.1:5000/api/courses/';
        
        const response = await fetch(url, {
          method: course ? 'PUT' : 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            ...formData,
            credits: parseFloat(formData.credits)
          })
        });

        if (response.ok) {
          onSave();
          onHide();
        }
      } catch (error) {
        console.error('Error saving course:', error);
      }
    }
    setValidated(true);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <Modal show={show} onHide={onHide}>
      <Modal.Header closeButton>
        <Modal.Title>
          {course ? 'Edit Course' : 'Add Course'}
        </Modal.Title>
      </Modal.Header>
      <Form noValidate validated={validated} onSubmit={handleSubmit}>
        <Modal.Body>
          <Form.Group className="mb-3">
            <Form.Label>Course ID</Form.Label>
            <Form.Control
              type="text"
              name="course_id"
              value={formData.course_id}
              onChange={handleChange}
              required
              disabled={!!course}
            />
            <Form.Control.Feedback type="invalid">
              Please provide a course ID.
            </Form.Control.Feedback>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Course Name</Form.Label>
            <Form.Control
              type="text"
              name="course_name"
              value={formData.course_name}
              onChange={handleChange}
              required
            />
            <Form.Control.Feedback type="invalid">
              Please provide a course name.
            </Form.Control.Feedback>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Credits</Form.Label>
            <Form.Control
              type="number"
              step="0.5"
              name="credits"
              value={formData.credits}
              onChange={handleChange}
              required
            />
            <Form.Control.Feedback type="invalid">
              Please provide credits.
            </Form.Control.Feedback>
          </Form.Group>
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

export default CourseModal;

