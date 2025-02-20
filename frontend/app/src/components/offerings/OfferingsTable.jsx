import React, { useState } from 'react';
import { Table, Button, Form, Row, Col } from 'react-bootstrap';

const getDayName = (day) => {
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  return days[day - 1];
};

const OfferingsTable = ({ offerings = [], onEdit, onDelete }) => {
  const [filters, setFilters] = useState({
    course_id: '',
    section_type: '',
    section_code: '',
    day_of_week: '',
    capacity: '',
    current_enrollment: '',
    term: '',
    academic_year: '2025-2026',
    status: ''
  });

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  if (!offerings) {
    return <div>No offerings available</div>;
  }

  const filteredOfferings = offerings.filter(offering => {
    return Object.entries(filters).every(([key, value]) => {
      if (!value) return true;
      if (key === 'day_of_week') {
        return getDayName(offering[key]).toLowerCase().includes(value.toLowerCase());
      }
      return offering[key].toString().toLowerCase().includes(value.toLowerCase());
    });
  });

  return (
    <>
      <Row className="mb-3">
        {Object.keys(filters).map(key => (
          <Col md={3} key={key}>
            <Form.Group>
              <Form.Label>{key.replace('_', ' ').toUpperCase()}</Form.Label>
              {key === 'academic_year' ? (
                <Form.Select
                  value={filters[key]}
                  onChange={(e) => handleFilterChange(key, e.target.value)}
                >
                  <option value="">All Years</option>
                  <option value="2024-2025">2024-2025</option>
                  <option value="2025-2026">2025-2026</option>
                  <option value="2026-2027">2026-2027</option>
                </Form.Select>
              ) : key === 'term' ? (
                <Form.Select
                  value={filters[key]}
                  onChange={(e) => handleFilterChange(key, e.target.value)}
                >
                  <option value="">All Terms</option>
                  <option value="FALL">Fall</option>
                  <option value="WINTER">Winter</option>
                </Form.Select>
              ) : key === 'section_type' ? (
                <Form.Select
                  value={filters[key]}
                  onChange={(e) => handleFilterChange(key, e.target.value)}
                >
                  <option value="">All Types</option>
                  <option value="LECTURE">Lecture</option>
                  <option value="LAB">Lab</option>
                  <option value="TUTORIAL">Tutorial</option>
                </Form.Select>
              ) : key === 'status' ? (
                <Form.Select
                  value={filters[key]}
                  onChange={(e) => handleFilterChange(key, e.target.value)}
                >
                  <option value="">All Statuses</option>
                  <option value="OPEN">Open</option>
                  <option value="FULL">Full</option>
                  <option value="CANCELLED">Cancelled</option>
                </Form.Select>
              ) : (
                <Form.Control
                  type="text"
                  value={filters[key]}
                  onChange={(e) => handleFilterChange(key, e.target.value)}
                  placeholder={`Filter by ${key.replace('_', ' ')}`}
                />
              )}
            </Form.Group>
          </Col>
        ))}
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
