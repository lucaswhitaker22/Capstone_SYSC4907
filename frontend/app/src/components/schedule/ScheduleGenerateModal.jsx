import React, { useState } from 'react';
import { Modal, Form, Button, Alert, Spinner, ListGroup } from 'react-bootstrap';

const ScheduleGenerateModal = ({ show, blocks, onHide, onGenerate }) => {
  const [selectedBlock, setSelectedBlock] = useState('');
  const [generatedSchedule, setGeneratedSchedule] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/schedules/block/${selectedBlock}`, {
        method: 'GET'
      });
      
      if (response.ok) {
        const data = await response.json();
        setGeneratedSchedule(data);
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Failed to generate schedule');
      }
    } catch (error) {
      setError('Error generating schedule');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/schedules/block/${selectedBlock}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ schedule: generatedSchedule })
      });
      
      if (response.ok) {
        await onGenerate();
        handleClose();
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Failed to save schedule');
      }
    } catch (error) {
      setError('Error saving schedule');
    } finally {
      setIsLoading(false);
    }
  };

  const getDayName = (day) => {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[day - 1];
  };

  const handleClose = () => {
    setSelectedBlock('');
    setGeneratedSchedule(null);
    setError(null);
    onHide();
  };

  return (
    <Modal show={show} onHide={handleClose} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Generate Block Schedule</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form.Group className="mb-3">
          <Form.Label>Select Block</Form.Label>
          <Form.Select
            value={selectedBlock}
            onChange={(e) => setSelectedBlock(e.target.value)}
            disabled={isLoading}
          >
            <option value="">Choose a block...</option>
            {blocks
              .filter(block => block.status !== 'LOCKED')
              .map(block => (
                <option key={block.block_id} value={block.block_id}>
                  Block {block.block_id} - Program {block.program_id} 
                  (Size: {block.block_size})
                </option>
              ))}
          </Form.Select>
        </Form.Group>

        {error && (
          <Alert variant="danger" className="mt-3">
            {error}
          </Alert>
        )}

        {generatedSchedule && (
          <div className="mt-4">
            <h5>Generated Schedule Preview:</h5>
            <ListGroup>
              {generatedSchedule.map((offering, index) => (
                <ListGroup.Item key={index}>
                  {offering.course_id} - {offering.section_type} {offering.section_code}
                  <br />
                  <small>
                    {getDayName(offering.day_of_week)} {offering.start_time}-{offering.end_time}
                  </small>
                </ListGroup.Item>
              ))}
            </ListGroup>
          </div>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Cancel
        </Button>
        {!generatedSchedule ? (
          <Button
            variant="primary"
            onClick={handleGenerate}
            disabled={!selectedBlock || isLoading}
          >
            {isLoading ? (
              <>
                <Spinner as="span" animation="border" size="sm" role="status" className="me-2" />
                Generating...
              </>
            ) : (
              'Preview Schedule'
            )}
          </Button>
        ) : (
          <Button
            variant="success"
            onClick={handleSave}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Spinner as="span" animation="border" size="sm" role="status" className="me-2" />
                Saving...
              </>
            ) : (
              'Save Schedule'
            )}
          </Button>
        )}
      </Modal.Footer>
    </Modal>
  );
};

export default ScheduleGenerateModal;
