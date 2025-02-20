import React, { useEffect, useState } from 'react';
import { Modal, Form, Button, Row, Col } from 'react-bootstrap';

const ProgramsModal = ({ show, program, onHide, onSave }) => {
  const initialFormData = {
    program_id: '',
    program_name: '',
    blocks_20_count: 0,
    blocks_10_count: 0,
    academic_year: '2025-2026'
  };

  const [formData, setFormData] = useState(initialFormData);
  const [validated, setValidated] = useState(false);
  useEffect(() => {
    if (program) {
      // When editing, take the Fall term counts (should be same as Winter)
      setFormData({
        program_id: program.program_id,
        program_name: program.program_name,
        blocks_20_count: program.blocks_20_count_fall,
        blocks_10_count: program.blocks_10_count_fall,
        academic_year: program.academic_year || '2025-2026'
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
                <Form.Label>Academic Year</Form.Label>
                <Form.Control
                  type="text"
                  name="academic_year"
                  value={formData.academic_year}
                  onChange={handleChange}
                  required
                  pattern="\d{4}-\d{4}"
                  placeholder="2025-2026"
                />
                <Form.Control.Feedback type="invalid">
                  Please provide a valid academic year (YYYY-YYYY).
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
          </Row>

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


          <h5 className="mb-3">Block Configuration (Applied to Both Terms)</h5>
          <Row>
            <Col md={6}>
              <Form.Group>
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
                  Please provide a valid number of blocks.
                </Form.Control.Feedback>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group>
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
                  Please provide a valid number of blocks.
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