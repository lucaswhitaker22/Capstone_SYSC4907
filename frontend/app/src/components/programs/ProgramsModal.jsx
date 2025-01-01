import React, { useEffect, useState } from 'react';
import { Modal, Form, Button, Row, Col } from 'react-bootstrap';

const ProgramsModal = ({ show, program, onHide, onSave }) => {
  const initialFormData = {
    program_id: '',
    program_name: '',
    total_enrollment: 0,
    blocks_20_count: 0,
    blocks_10_count: 0
  };

  const [formData, setFormData] = useState(initialFormData);
  const [validated, setValidated] = useState(false);

  useEffect(() => {
    if (program) {
      setFormData({
        program_id: program.program_id,
        program_name: program.program_name,
        total_enrollment: program.total_enrollment,
        blocks_20_count: program.blocks_20_count,
        blocks_10_count: program.blocks_10_count
      });
    } else {
      setFormData(initialFormData);
    }
    setValidated(false);
  }, [program, show]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const numericFields = ['total_enrollment', 'blocks_20_count', 'blocks_10_count'];
    
    setFormData(prev => ({
      ...prev,
      [name]: numericFields.includes(name) ? parseInt(value) || 0 : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    
    if (form.checkValidity()) {
      onSave(formData);
    }
    setValidated(true);
  };

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>
          {program ? 'Edit Program' : 'Create New Program'}
        </Modal.Title>
      </Modal.Header>
      <Form noValidate validated={validated} onSubmit={handleSubmit}>
        <Modal.Body>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Program ID</Form.Label>
                <Form.Control
                  type="text"
                  name="program_id"
                  value={formData.program_id}
                  onChange={handleChange}
                  required
                  disabled={program}
                />
                <Form.Control.Feedback type="invalid">
                  Please provide a program ID.
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Program Name</Form.Label>
                <Form.Control
                  type="text"
                  name="program_name"
                  value={formData.program_name}
                  onChange={handleChange}
                  required
                />
                <Form.Control.Feedback type="invalid">
                  Please provide a program name.
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
          </Row>

          <Row>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>Total Enrollment</Form.Label>
                <Form.Control
                  type="number"
                  name="total_enrollment"
                  value={formData.total_enrollment}
                  onChange={handleChange}
                  required
                  min="0"
                />
                <Form.Control.Feedback type="invalid">
                  Please provide a valid enrollment number.
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>20-Student Blocks</Form.Label>
                <Form.Control
                  type="number"
                  name="blocks_20_count"
                  value={formData.blocks_20_count}
                  onChange={handleChange}
                  required
                  min="0"
                />
                <Form.Control.Feedback type="invalid">
                  Please provide a valid number of 20-student blocks.
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>10-Student Blocks</Form.Label>
                <Form.Control
                  type="number"
                  name="blocks_10_count"
                  value={formData.blocks_10_count}
                  onChange={handleChange}
                  required
                  min="0"
                />
                <Form.Control.Feedback type="invalid">
                  Please provide a valid number of 10-student blocks.
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
          </Row>
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

export default ProgramsModal;
