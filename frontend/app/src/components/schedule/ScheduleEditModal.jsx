import React, { useState, useEffect } from 'react';
import { Modal, Form, Button, ListGroup, Alert, Spinner, Badge, Tabs, Tab, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { InfoCircle } from 'react-bootstrap-icons';

const ScheduleEditModal = ({ show, blockId, offerings, onHide, onSave }) => {
  const [blockSchedule, setBlockSchedule] = useState([]);
  const [selectedOffering, setSelectedOffering] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [blockTerm, setBlockTerm] = useState(null);

  // Helper function to create tooltips
  const renderTooltip = (text) => (
    <OverlayTrigger
      placement="right"
      overlay={<Tooltip>{text}</Tooltip>}
    >
      <InfoCircle className="ms-2" />
    </OverlayTrigger>
  );

  useEffect(() => {
    if (show && blockId) {
      fetchBlockSchedule();
      fetchBlockDetails();
    }
  }, [show, blockId]);

  const fetchBlockDetails = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/blocks/${blockId}`);
      if (response.ok) {
        const data = await response.json();
        setBlockTerm(data.term);
      }
    } catch (error) {
      setError('Error fetching block details');
    }
  };

  const fetchBlockSchedule = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/schedules/block/${blockId}`);
      if (response.ok) {
        const data = await response.json();
        setBlockSchedule(data);
      }
    } catch (error) {
      setError('Error fetching schedule');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddOffering = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/schedules/block/${blockId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          offering_id: selectedOffering,
          term: blockTerm
        }),
      });

      const data = await response.json();
      if (response.ok) {
        await fetchBlockSchedule();
        setSelectedOffering('');
      } else {
        setError(data.message || 'Error adding offering');
      }
    } catch (error) {
      setError('Error adding offering');
    }
  };

  const handleRemoveOffering = async (offeringId) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:5000/api/schedules/block/${blockId}/offering/${offeringId}`,
        { method: 'DELETE' }
      );
      if (response.ok) {
        await fetchBlockSchedule();
      }
    } catch (error) {
      setError('Error removing offering');
    }
  };

  const getDayName = (day) => {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[day - 1];
  };

  // Filter offerings by term
  const termOfferings = offerings.filter(offering => offering.term === blockTerm);

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>
          Edit Block Schedule
          {renderTooltip("Manually assign or remove courses from this teaching block")}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {blockTerm && (
          <h5 className="mb-3">
            {blockTerm} Term
            {renderTooltip(`Courses for the ${blockTerm} academic term`)}
          </h5>
        )}
        
        {isLoading ? (
          <div className="text-center p-4">
            <Spinner animation="border" />
          </div>
        ) : (
          <>
            <Form.Group className="mb-3">
              <Form.Label>
                Add Course Offering ({blockTerm} Term)
                {renderTooltip("Select a course to add to this block's schedule")}
              </Form.Label>
              <Form.Select
                value={selectedOffering}
                onChange={(e) => setSelectedOffering(e.target.value)}
              >
                <option value="">Select an offering</option>
                {termOfferings.map(offering => (
                  <option key={offering.offering_id} value={offering.offering_id}>
                    {offering.course_id} - {offering.section_type} {offering.section_code}
                    ({getDayName(offering.day_of_week)} {offering.start_time}-{offering.end_time})
                  </option>
                ))}
              </Form.Select>
            </Form.Group>

            <Button 
              variant="primary" 
              onClick={handleAddOffering}
              disabled={!selectedOffering}
              className="mb-3"
            >
              Add to Schedule
              {renderTooltip("Assign the selected course to this block")}
            </Button>

            {error && <Alert variant="danger">{error}</Alert>}

            <h5 className="mt-4 mb-3">
              Current Schedule
              {renderTooltip("Courses currently assigned to this block")}
            </h5>

            <ListGroup>
              {blockSchedule.length === 0 ? (
                <Alert variant="info">No courses assigned to this block yet</Alert>
              ) : (
                blockSchedule.map(offering => (
                  <ListGroup.Item
                    key={offering.offering_id}
                    className="d-flex justify-content-between align-items-center"
                  >
                    <div>
                      <Badge bg="primary" className="me-2">{offering.section_type}</Badge>
                      {offering.course_id} - {offering.section_code}
                      <br />
                      <small>
                        {getDayName(offering.day_of_week)} {offering.start_time}-{offering.end_time}
                      </small>
                    </div>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleRemoveOffering(offering.offering_id)}
                    >
                      Remove
                      {renderTooltip("Remove this course from the block's schedule")}
                    </Button>
                  </ListGroup.Item>
                ))
              )}
            </ListGroup>
          </>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
          {renderTooltip("Close this dialog and return to the schedule list")}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ScheduleEditModal;
