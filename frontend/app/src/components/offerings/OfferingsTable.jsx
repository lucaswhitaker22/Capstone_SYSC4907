import React, { useState } from 'react';
import { Table, Button, Form, Card, Collapse, Row, Col } from 'react-bootstrap';

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
  const [showFilters, setShowFilters] = useState(false);

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
        return offering[key] === parseInt(value);
      }
      return offering[key].toString().toLowerCase().includes(value.toLowerCase());
    });
  });

  return (
    <>
      <Button
        onClick={() => setShowFilters(!showFilters)}
        aria-controls="filter-collapse"
        aria-expanded={showFilters}
        className="mb-3"
      >
        {showFilters ? 'Hide Filters' : 'Show Filters'}
      </Button>
      <Collapse in={showFilters}>
        <div id="filter-collapse">
          <Card className="mb-3">
            <Card.Body>
              <Row>
                <Col md={3}>
                  <Form.Group>
                    <Form.Label>Course ID</Form.Label>
                    <Form.Control
                      type="text"
                      value={filters.course_id}
                      onChange={(e) => handleFilterChange('course_id', e.target.value)}
                      placeholder="Filter by course ID"
                    />
                  </Form.Group>
                </Col>
                <Col md={3}>
                  <Form.Group>
                    <Form.Label>Section Type</Form.Label>
                    <Form.Select
                      value={filters.section_type}
                      onChange={(e) => handleFilterChange('section_type', e.target.value)}
                    >
                      <option value="">All Types</option>
                      <option value="LECTURE">Lecture</option>
                      <option value="LAB">Lab</option>
                      <option value="TUTORIAL">Tutorial</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={2}>
                  <Form.Group>
                    <Form.Label>Section Code</Form.Label>
                    <Form.Control
                      type="text"
                      value={filters.section_code}
                      onChange={(e) => handleFilterChange('section_code', e.target.value)}
                      placeholder="Filter by section"
                    />
                  </Form.Group>
                </Col>
                <Col md={2}>
                  <Form.Group>
                    <Form.Label>Day</Form.Label>
                    <Form.Select
                      value={filters.day_of_week}
                      onChange={(e) => handleFilterChange('day_of_week', e.target.value)}
                    >
                      <option value="">All Days</option>
                      {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'].map((day, index) => (
                        <option key={day} value={index + 2}>{day}</option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={2}>
                  <Form.Group>
                    <Form.Label>Term</Form.Label>
                    <Form.Select
                      value={filters.term}
                      onChange={(e) => handleFilterChange('term', e.target.value)}
                    >
                      <option value="">All Terms</option>
                      <option value="FALL">Fall</option>
                      <option value="WINTER">Winter</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </div>
      </Collapse>

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
