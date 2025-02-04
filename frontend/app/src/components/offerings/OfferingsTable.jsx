import React, { useState } from 'react';
import { Table, Button, Form, Row, Col } from 'react-bootstrap';

const getDayName = (day) => {
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  return days[day - 1];
};

const OfferingsTable = ({ offerings = [], onEdit, onDelete }) => {
  const [termFilter, setTermFilter] = useState('');
  const [yearFilter, setYearFilter] = useState('2025-2026');

  if (!offerings) {
    return <div>No offerings available</div>;
  }

  const filteredOfferings = offerings.filter(offering => {
    if (termFilter && offering.term !== termFilter) return false;
    if (yearFilter && offering.academic_year !== yearFilter) return false;
    return true;
  });

  return (
    <>
      <Row className="mb-3">
        <Col md={3}>
          <Form.Group>
            <Form.Label>Term</Form.Label>
            <Form.Select
              value={termFilter}
              onChange={(e) => setTermFilter(e.target.value)}
            >
              <option value="">All Terms</option>
              <option value="FALL">Fall</option>
              <option value="WINTER">Winter</option>
            </Form.Select>
          </Form.Group>
        </Col>
        <Col md={3}>
          <Form.Group>
            <Form.Label>Academic Year</Form.Label>
            <Form.Select 
                value={yearFilter}
                onChange={(e) => setYearFilter(e.target.value)}
            >
                <option value="2024-2025">2024-2025</option>
                <option value="2025-2026">2025-2026</option>
                <option value="2026-2027">2026-2027</option>
            </Form.Select>
          </Form.Group>
        </Col>
      </Row>

      <Table striped bordered hover responsive>
        <thead>
          <tr>
            <th>Course ID</th>
            <th>Section Type</th>
            <th>Section Code</th>
            <th>Day</th>
            <th>Time</th>
            <th>Capacity</th>
            <th>Enrollment</th>
            <th>Term</th>
            <th>Academic Year</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filteredOfferings.map((offering) => (
            <tr key={offering.offering_id}>
              <td>{offering.course_id}</td>
              <td>{offering.section_type}</td>
              <td>{offering.section_code}</td>
              <td>{getDayName(offering.day_of_week)}</td>
              <td>{`${offering.start_time}-${offering.end_time}`}</td>
              <td>{offering.capacity}</td>
              <td>{offering.current_enrollment}</td>
              <td>{offering.term}</td>
              <td>{offering.academic_year}</td>
              <td>{offering.status}</td>
              <td>
                <Button
                  variant="primary"
                  size="sm"
                  className="me-2"
                  onClick={() => onEdit(offering)}
                >
                  Edit
                </Button>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => onDelete(offering.offering_id)}
                >
                  Delete
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </>
  );
};

export default OfferingsTable;
