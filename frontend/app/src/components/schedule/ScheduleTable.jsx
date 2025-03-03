import React, { useState, useEffect } from 'react';
import { Table, Button, Badge, Spinner, Tabs, Tab } from 'react-bootstrap';

const ScheduleTable = ({
  schedules = [],
  onView,
  onEdit,
  onValidate,
  onDelete,
  isLoading,
  onGenerate,
  onSelectionChange 
}) => {
  const [selectedRows, setSelectedRows] = useState([]);
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
    rating = rating/2;
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

  const handleRowSelection = (blockId) => {
    const newSelectedRows = selectedRows.includes(blockId)
      ? selectedRows.filter(id => id !== blockId)
      : [...selectedRows, blockId];
    setSelectedRows(newSelectedRows);
    onSelectionChange(newSelectedRows);
  };


  const handleSelectAll = (event) => {
    const newSelectedRows = event.target.checked ? schedules.map(s => s.block_id) : [];
    setSelectedRows(newSelectedRows);
    onSelectionChange(newSelectedRows);
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

  const renderScheduleTable = (termSchedules) => (
    <Table striped bordered hover responsive>
      <thead>
        <tr>
          <th>
            <input
              type="checkbox"
              onChange={handleSelectAll}
              checked={selectedRows.length === schedules.length}
            />
          </th>
          <th>Block ID</th>
          <th>Program</th>
          <th>Term</th>
          <th>Courses</th>
          <th>Days</th>
          <th>Rating</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {termSchedules.map((schedule) => (
          <tr key={schedule.block_id}>
                        <td>
              <input
                type="checkbox"
                onChange={() => handleRowSelection(schedule.block_id)}
                checked={selectedRows.includes(schedule.block_id)}
              />
            </td>

            <td>Block {schedule.block_id}</td>
            <td>{schedule.program_id}</td>
            <td>
              <Badge bg={schedule.term === 'FALL' ? 'warning' : 'info'}>
                {schedule.term}
              </Badge>
            </td>
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
                  variant="success"
                  size="sm"
                  onClick={() => onGenerate(schedule.block_id)}
                >
                  Generate
                </Button>
                <Button
                  variant="info"
                  size="sm"
                  onClick={() => onValidate(schedule.block_id)}
                >
                  Validate
                </Button>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => onDelete(schedule.block_id)}
                >
                  Clear
                </Button>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </Table>
  );

  // Split schedules by term
  const fallSchedules = schedules.filter(s => s.term === 'FALL');
  const winterSchedules = schedules.filter(s => s.term === 'WINTER');

  return (
    <Tabs defaultActiveKey="fall" className="mb-3">
      <Tab eventKey="fall" title="Fall Term">
        {renderScheduleTable(fallSchedules)}
      </Tab>
      <Tab eventKey="winter" title="Winter Term">
        {renderScheduleTable(winterSchedules)}
      </Tab>
    </Tabs>
  );
};

export default ScheduleTable;
