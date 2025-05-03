import React, { useState, useEffect } from 'react';
import { Modal, Form, Button, Alert, Spinner, ListGroup, Tabs, Tab } from 'react-bootstrap';

const API_URL = 'http://127.0.0.1:5000/api';

const CourseConflictModal = ({ show, onHide }) => {
  const [offerings, setOfferings] = useState([]);
  const [selectedScheduleOfferings, setSelectedScheduleOfferings] = useState([]);
  const [newOffering, setNewOffering] = useState('');
  const [conflicts, setConflicts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingOfferings, setIsLoadingOfferings] = useState(true);
  const [selectedTerm, setSelectedTerm] = useState('FALL');
  const [selectedYear, setSelectedYear] = useState('2025-2026');

  useEffect(() => {
    if (show) {
      fetchOfferings();
      setConflicts([]);
      setSelectedScheduleOfferings([]);
      setNewOffering('');
    }
  }, [show, selectedTerm, selectedYear]);

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

  const handleScheduleOfferingsSelect = (e) => {
    const selectedOptions = Array.from(e.target.selectedOptions, option => option.value);
    setSelectedScheduleOfferings(selectedOptions);
  };

  const checkConflicts = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/conflicts/schedule/check-course`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          schedule_offering_ids: selectedScheduleOfferings,
          new_offering_id: newOffering,
          term: selectedTerm,
          academic_year: selectedYear
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

  // Filter offerings by term and year
  const filteredOfferings = offerings.filter(
    offering => offering.term === selectedTerm && offering.academic_year === selectedYear
  );

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Check Course Conflicts</Modal.Title>
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
            <div className="mb-3 d-flex gap-3">
              <Form.Group style={{ width: '200px' }}>
                <Form.Label>Term</Form.Label>
                <Form.Select
                  value={selectedTerm}
                  onChange={(e) => {
                    setSelectedTerm(e.target.value);
                    setSelectedScheduleOfferings([]);
                    setNewOffering('');
                    setConflicts([]);
                  }}
                >
                  <option value="FALL">Fall</option>
                  <option value="WINTER">Winter</option>
                </Form.Select>
              </Form.Group>

              <Form.Group style={{ width: '200px' }}>
                <Form.Label>Academic Year</Form.Label>
                <Form.Select
                  value={selectedYear}
                  onChange={(e) => {
                    setSelectedYear(e.target.value);
                    setSelectedScheduleOfferings([]);
                    setNewOffering('');
                    setConflicts([]);
                  }}
                >
                  <option value="2024-2025">2024-2025</option>
                  <option value="2025-2026">2025-2026</option>
                  <option value="2026-2027">2026-2027</option>
                </Form.Select>
              </Form.Group>
            </div>

            <Form.Group className="mb-3">
              <Form.Label>Select Existing Schedule Offerings ({selectedTerm} {selectedYear})</Form.Label>
              <Form.Select 
                multiple 
                size={6}
                value={selectedScheduleOfferings}
                onChange={handleScheduleOfferingsSelect}
              >
                {filteredOfferings.map(offering => (
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

            <Form.Group className="mb-3">
              <Form.Label>Select New Course Offering ({selectedTerm} {selectedYear})</Form.Label>
              <Form.Select
                value={newOffering}
                onChange={(e) => setNewOffering(e.target.value)}
              >
                <option value="">Select an offering</option>
                {filteredOfferings.map(offering => (
                  <option key={offering.offering_id} value={offering.offering_id}>
                    {offering.course_id} - {offering.section_type} {offering.section_code}
                    ({getDayName(offering.day_of_week)} {offering.start_time}-{offering.end_time})
                  </option>
                ))}
              </Form.Select>
            </Form.Group>

            {conflicts.length > 0 && (
              <Alert variant="danger">
                <Alert.Heading>Conflicts Found ({selectedTerm} {selectedYear})</Alert.Heading>
                <ListGroup>
                  {conflicts.map((conflict, index) => (
                    <ListGroup.Item key={index} variant="danger">
                      Conflict on {getDayName(conflict.day_of_week)}:<br />
                      New course {conflict.new_course_id} ({conflict.new_time}) conflicts with<br />
                      Existing course {conflict.existing_course_id} ({conflict.existing_time})
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              </Alert>
            )}

            {conflicts.length === 0 && selectedScheduleOfferings.length > 0 && newOffering && !isLoading && (
              <Alert variant="success">
                No conflicts found for the selected course in {selectedTerm} {selectedYear}.
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
          disabled={selectedScheduleOfferings.length === 0 || !newOffering || isLoading}
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

export default CourseConflictModal;
