import React, { useEffect, useState } from 'react';
import { Modal, Form, Button, Table, Row, Col } from 'react-bootstrap';

const ProgramRequirementsModal = ({ show, programId, onHide }) => {
    const [requirements, setRequirements] = useState([]);
    const [courses, setCourses] = useState([]); // Add courses state
    const [newRequirement, setNewRequirement] = useState({
      course_id: '',
      term: ''
    });
    const [isLoading, setIsLoading] = useState(true);

    const fetchRequirements = async () => {
        try {
          const response = await fetch(`http://127.0.0.1:5000/api/requirements/program/${programId}`);
          if (response.ok) {
            const data = await response.json();
            setRequirements(data);
          }
        } catch (error) {
          console.error('Error fetching requirements:', error);
        } finally {
          setIsLoading(false);
        }
      };
    
  // Add function to fetch courses
  const fetchCourses = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/courses');
      if (response.ok) {
        const data = await response.json();
        setCourses(data);
      }
    } catch (error) {
      console.error('Error fetching courses:', error);
    }
  };
  useEffect(() => {
    if (show && programId) {
      fetchRequirements();
      fetchCourses(); // Fetch courses when modal opens
    }
  }, [show, programId]);

  const handleAddRequirement = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://127.0.0.1:5000/api/requirements', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          program_id: programId,
          ...newRequirement,
          term: parseInt(newRequirement.term)
        }),
      });

      if (response.ok) {
        await fetchRequirements();
        setNewRequirement({ course_id: '', term: '' });
      } else {
        const error = await response.json();
        alert(error.error || 'Error adding requirement');
      }
    } catch (error) {
      console.error('Error adding requirement:', error);
    }
  };

  const handleDeleteRequirement = async (requirementId) => {
    if (window.confirm('Are you sure you want to delete this requirement?')) {
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/requirements/${requirementId}`, {
          method: 'DELETE'
        });
        if (response.ok) {
          await fetchRequirements();
        }
      } catch (error) {
        console.error('Error deleting requirement:', error);
      }
    }
  };

  const handleUpdateRequirement = async (requirementId, updatedData) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/requirements/${requirementId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedData),
      });

      if (response.ok) {
        await fetchRequirements();
      }
    } catch (error) {
      console.error('Error updating requirement:', error);
    }
  };

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Program Requirements</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleAddRequirement} className="mb-4">
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Course</Form.Label>
                <Form.Select
                  value={newRequirement.course_id}
                  onChange={(e) => setNewRequirement(prev => ({
                    ...prev,
                    course_id: e.target.value
                  }))}
                  required
                >
                  <option value="">Select a course...</option>
                  {courses.map(course => (
                    <option key={course.course_id} value={course.course_id}>
                      {course.course_id} - {course.course_name}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>Term</Form.Label>
                <Form.Control
                  type="number"
                  value={newRequirement.term}
                  onChange={(e) => setNewRequirement(prev => ({
                    ...prev,
                    term: e.target.value
                  }))}
                  required
                  min="1"
                />
              </Form.Group>
            </Col>
            <Col md={2} className="d-flex align-items-end">
              <Button type="submit" variant="primary" className="mb-3">
                Add
              </Button>
            </Col>
          </Row>
        </Form>

        <Table striped bordered hover>
          <thead>
            <tr>
              <th>Course ID</th>
              <th>Term</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {requirements.map((req) => (
              <tr key={`${req.program_id}-${req.course_id}`}>
                <td>{req.course_id}</td>
                <td>{req.term}</td>
                <td>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleDeleteRequirement(req.requirement_id)}
                    className="me-2"
                  >
                    Delete
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleUpdateRequirement(req.requirement_id, {
                      term: parseInt(prompt('Enter new term:', req.term))
                    })}
                  >
                    Edit Term
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ProgramRequirementsModal;
