import React, { useEffect, useState } from 'react';
import { Modal, Form, Button, Row, Col } from 'react-bootstrap';

const BlocksModal = ({ show, block, onHide, onSave }) => {
  const initialFormData = {
    block_id: '',
    program_id: '',
    block_size: '10',
    term: '',
    academic_year: '',
    status: 'DRAFT'
  };

  const [formData, setFormData] = useState(initialFormData);
  const [validated, setValidated] = useState(false);
  const [programs, setPrograms] = useState([]);

  useEffect(() => {
    if (show) {
      fetchPrograms();
    }
  }, [show]);

  useEffect(() => {
    if (block) {
      setFormData({
        block_id: block.block_id,
        program_id: block.program_id,
        block_size: block.block_size.toString(),
        term: block.term,
        academic_year: block.academic_year,
        status: block.status
      });
    } else {
      setFormData(initialFormData);
    }
    setValidated(false);
  }, [block, show]);

  const API_URL = 'http://127.0.0.1:5000/api';

  const fetchPrograms = async () => {
    try {
      const response = await fetch(`${API_URL}/programs`);
      const data = await response.json();
      setPrograms(data);
    } catch (error) {
      console.error('Error fetching programs:', error);
    }
  };

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
        block_size: parseInt(formData.block_size)
      });
    }
    setValidated(true);
  };

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>
          {block ? 'Edit Block' : 'Create New Block'}
        </Modal.Title>
      </Modal.Header>
      <Form noValidate validated={validated} onSubmit={handleSubmit}>
        <Modal.Body>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Block ID</Form.Label>
                <Form.Control
                  type="text"
                  name="block_id"
                  value={formData.block_id}
                  onChange={handleChange}
                  required
                  disabled={block}
                />
                <Form.Control.Feedback type="invalid">
                  Please provide a block ID.
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Program</Form.Label>
                <Form.Select
                  name="program_id"
                  value={formData.program_id}
                  onChange={handleChange}
                  required
                  disabled={block}
                >
                  <option value="">Select a program</option>
                  {programs.map(program => (
                    <option key={program.program_id} value={program.program_id}>
                      {program.program_id} - {program.program_name}
                    </option>
                  ))}
                </Form.Select>
                <Form.Control.Feedback type="invalid">
                  Please select a program.
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
          </Row>

          <Row>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>Block Size</Form.Label>
                <Form.Select
                  name="block_size"
                  value={formData.block_size}
                  onChange={handleChange}
                  required
                >
                  <option value="10">10</option>
                  <option value="20">20</option>
                </Form.Select>
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

          {block && (
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
                    <option value="DRAFT">Draft</option>
                    <option value="PUBLISHED">Published</option>
                    <option value="LOCKED">Locked</option>
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

export default BlocksModal;
