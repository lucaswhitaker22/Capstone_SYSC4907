import React from 'react';
import { Table, Button, Badge, Spinner } from 'react-bootstrap';

const ScheduleTable = ({ schedules = [], onView, onEdit, onValidate, isLoading }) => {
  if (isLoading) {
    return (
      <div className="text-center p-4">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading schedules...</span>
        </Spinner>
      </div>
    );
  }

  if (!schedules.length) {
    return <div className="text-center p-4">No schedules available</div>;
  }

  const getRatingBadge = (rating) => {
    if (!rating) return <Badge bg="secondary">Not Rated</Badge>;
    
    let variant;
    if (rating >= 80) variant = 'success';
    else if (rating >= 60) variant = 'warning';
    else variant = 'danger';

    return (
      <Badge bg={variant}>
        {rating.toFixed(1)}%
      </Badge>
    );
  };

  const getCoursesCount = (offerings) => {
    if (!offerings) return 0;
    return offerings.length;
  };

  const getDaysString = (offerings) => {
    if (!offerings || !offerings.length) return 'No days scheduled';
    
    const days = [...new Set(offerings.map(o => o.day_of_week))].sort();
    const dayNames = days.map(day => {
      const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
      return daysOfWeek[day - 1];
    });
    
    return dayNames.join(', ');
  };

  return (
    <Table striped bordered hover responsive>
      <thead>
        <tr>
          <th>Block ID</th>
          <th>Program</th>
          <th>Courses</th>
          <th>Days</th>
          <th>Rating</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {schedules.map((schedule) => (
          <tr key={schedule.block_id}>
            <td>Block {schedule.block_id}</td>
            <td>{schedule.program_id}</td>
            <td>
              <Badge bg="info">
                {getCoursesCount(schedule.offerings)} courses
              </Badge>
            </td>
            <td>{getDaysString(schedule.offerings)}</td>
            <td>{getRatingBadge(schedule.rating)}</td>
            <td>
              <div className="d-flex gap-2">
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => onView(schedule.block_id)}
                >
                  View
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => onEdit(schedule.block_id)}
                >
                  Edit
                </Button>
                <Button
                  variant="info"
                  size="sm"
                  onClick={() => onValidate(schedule.block_id)}
                >
                  Validate
                </Button>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};

export default ScheduleTable;
