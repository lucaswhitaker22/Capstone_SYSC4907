import React from 'react';
import { Table, Button } from 'react-bootstrap';

const getDayName = (day) => {
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  return days[day - 1];
};

const OfferingsTable = ({ offerings = [], onEdit, onDelete }) => {
  if (!offerings) {
    return <div>No offerings available</div>;
  }

  return (
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
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {offerings.map((offering) => (
          <tr key={offering.offering_id}>
            <td>{offering.course_id}</td>
            <td>{offering.section_type}</td>
            <td>{offering.section_code}</td>
            <td>{getDayName(offering.day_of_week)}</td>
            <td>{`${offering.start_time}-${offering.end_time}`}</td>
            <td>{offering.capacity}</td>
            <td>{offering.current_enrollment}</td>
            <td>{`${offering.term} ${offering.academic_year}`}</td>
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
  );
};

export default OfferingsTable;
