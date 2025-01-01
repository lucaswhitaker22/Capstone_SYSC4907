import React, { useState, useEffect } from 'react';
import { Modal, Form, Button, Alert, Spinner, ListGroup } from 'react-bootstrap';

const API_URL = 'http://127.0.0.1:5000/api';

const ScheduleConflictModal = ({ show, onHide }) => {
  const [offerings, setOfferings] = useState([]);
  const [selectedOfferings, setSelectedOfferings] = useState([]);
  const [conflicts, setConflicts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingOfferings, setIsLoadingOfferings] = useState(true);

  useEffect(() => {
    if (show) {
      fetchOfferings();
      setConflicts([]);
      setSelectedOfferings([]);
    }
  }, [show]);

  const fetchOfferings = async () => {
    try {
      const response = await fetch(`${API_URL}/offerings`);
      if (response.ok) {
        const data = await response.json();
        setOfferings(data);
      }
    } catch (error) {
      console.error('Error fetching offerings:', error);
    } finally {
      setIsLoadingOfferings(false);
    }
  };

  const handleOfferingSelect = (e) => {
    const selectedOptions = Array.from(e.target.selectedOptions, option => option.value);
    setSelectedOfferings(selectedOptions);
  };

  const checkConflicts = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/conflicts/schedule/conflicts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          offering_ids: selectedOfferings
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setConflicts(data.conflicts);
      }
    } catch (error) {
      console.error('Error checking conflicts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getDayName = (day) => {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[day - 1];
  };

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Check Schedule Conflicts</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {isLoadingOfferings ? (
          <div className="text-center p-4">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading offerings...</span>
            </Spinner>
          </div>
        ) : (
          <>
            <Form.Group className="mb-3">
              <Form.Label>Select Multiple Offerings</Form.Label>
              <Form.Select 
                multiple 
                size={6}
                value={selectedOfferings}
                onChange={handleOfferingSelect}
              >
                {offerings.map(offering => (
                  <option key={offering.offering_id} value={offering.offering_id}>
                    {offering.course_id} - {offering.section_type} {offering.section_code}
                    ({getDayName(offering.day_of_week)} {offering.start_time}-{offering.end_time})
                  </option>
                ))}
              </Form.Select>
              <Form.Text className="text-muted">
                Hold Ctrl/Cmd to select multiple offerings
              </Form.Text>
            </Form.Group>

            {conflicts.length > 0 && (
              <div className="mt-3">
                <Alert variant="danger">
                  <Alert.Heading>Conflicts Found</Alert.Heading>
                  <ListGroup>
                    {conflicts.map((conflict, index) => (
                      <ListGroup.Item key={index} variant="danger">
                        Conflict on {getDayName(conflict.day)}:<br />
                        {conflict.course1_id} ({conflict.time1}) conflicts with<br />
                        {conflict.course2_id} ({conflict.time2})
                      </ListGroup.Item>
                    ))}
                  </ListGroup>
                </Alert>
              </div>
            )}

            {conflicts.length === 0 && selectedOfferings.length > 0 && !isLoading && (
              <Alert variant="success">
                No conflicts found in the selected offerings.
              </Alert>
            )}
          </>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>Close</Button>
        <Button 
          variant="primary" 
          onClick={checkConflicts}
          disabled={selectedOfferings.length < 2 || isLoading}
        >
          {isLoading ? (
            <>
              <Spinner
                as="span"
                animation="border"
                size="sm"
                role="status"
                className="me-2"
              />
              Checking...
            </>
          ) : (
            'Check Conflicts'
          )}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ScheduleConflictModal;
