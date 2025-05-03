import React, { useState, useEffect } from 'react';
import { Modal, Form, Button, Alert, Spinner } from 'react-bootstrap';

const API_URL = 'http://127.0.0.1:5000/api';

const OfferingConflictModal = ({ show, onHide }) => {
  const [offerings, setOfferings] = useState([]);
  const [offering1, setOffering1] = useState('');
  const [offering2, setOffering2] = useState('');
  const [conflict, setConflict] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingOfferings, setIsLoadingOfferings] = useState(true);
  const [selectedTerm, setSelectedTerm] = useState('FALL');
  const [selectedYear, setSelectedYear] = useState('2025-2026');

  useEffect(() => {
    if (show) {
      fetchOfferings();
      resetForm();
    }
  }, [show, selectedTerm, selectedYear]);

  const resetForm = () => {
    setConflict(null);
    setOffering1('');
    setOffering2('');
  };

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

  const checkConflict = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `${API_URL}/conflicts/offerings/${offering1}/${offering2}`
      );
      if (response.ok) {
        const data = await response.json();
        setConflict(data);
      }
    } catch (error) {
      console.error('Error checking conflict:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderOfferingOption = (offering) => (
    <option key={offering.offering_id} value={offering.offering_id}>
      {offering.course_id} - {offering.section_type} {offering.section_code} 
      ({getDayName(offering.day_of_week)} {offering.start_time}-{offering.end_time})
    </option>
  );

  const getDayName = (day) => {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[day - 1];
  };

  // Filter offerings by term and year
  const filteredOfferings = offerings.filter(
    offering => offering.term === selectedTerm && offering.academic_year === selectedYear
  );

  return (
    <Modal show={show} onHide={onHide}>
      <Modal.Header closeButton>
        <Modal.Title>Check Offering Conflicts</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {isLoadingOfferings ? (
          <div className="text-center p-4">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading offerings...</span>
            </Spinner>
          </div>
        ) : (
          <Form>
            <div className="mb-3 d-flex gap-3">
              <Form.Group style={{ width: '200px' }}>
                <Form.Label>Term</Form.Label>
                <Form.Select
                  value={selectedTerm}
                  onChange={(e) => {
                    setSelectedTerm(e.target.value);
                    resetForm();
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
                    resetForm();
                  }}
                >
                  <option value="2024-2025">2024-2025</option>
                  <option value="2025-2026">2025-2026</option>
                  <option value="2026-2027">2026-2027</option>
                </Form.Select>
              </Form.Group>
            </div>

            <Form.Group className="mb-3">
              <Form.Label>First Offering ({selectedTerm} {selectedYear})</Form.Label>
              <Form.Select
                value={offering1}
                onChange={(e) => {
                  setOffering1(e.target.value);
                  setOffering2('');
                  setConflict(null);
                }}
              >
                <option value="">Select an offering</option>
                {filteredOfferings.map(renderOfferingOption)}
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Second Offering ({selectedTerm} {selectedYear})</Form.Label>
              <Form.Select
                value={offering2}
                onChange={(e) => {
                  setOffering2(e.target.value);
                  setConflict(null);
                }}
                disabled={!offering1}
              >
                <option value="">Select an offering</option>
                {filteredOfferings
                  .filter(o => o.offering_id !== offering1)
                  .map(renderOfferingOption)}
              </Form.Select>
            </Form.Group>
          </Form>
        )}
        {conflict && (
          <Alert variant={conflict.has_conflict ? 'danger' : 'success'}>
            {conflict.has_conflict ? (
              <>
                Time conflict detected in {selectedTerm} {selectedYear}:<br/>
                {conflict.offering1.course_id} conflicts with {conflict.offering2.course_id}
              </>
            ) : (
              `No time conflicts detected between these offerings in ${selectedTerm} ${selectedYear}`
            )}
          </Alert>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>Close</Button>
        <Button 
          variant="primary" 
          onClick={checkConflict}
          disabled={!offering1 || !offering2 || isLoading}
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
            'Check Conflict'
          )}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default OfferingConflictModal;
