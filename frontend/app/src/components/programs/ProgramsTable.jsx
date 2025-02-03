import React from 'react';
import { Table, Button, Badge, Spinner } from 'react-bootstrap';

const ProgramsTable = ({ programs = [], onEdit, onDelete, isLoading, onViewRequirements, onViewSchedules }) => {
  if (isLoading) {
    return (
      <div className="text-center p-4">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
  }

  if (!programs.length) {
    return <div className="text-center p-4">No programs available</div>;
  }

  return (
    <Table striped bordered hover responsive>
      <thead>
        <tr>
          <th rowSpan="2">Program ID</th>
          <th rowSpan="2">Program Name</th>
          <th rowSpan="2">Total Enrollment</th>
          <th colSpan="2" className="text-center">Fall Blocks</th>
          <th colSpan="2" className="text-center">Winter Blocks</th>
          <th rowSpan="2">Actions</th>
        </tr>
        <tr>
          <th>20-Student</th>
          <th>10-Student</th>
          <th>20-Student</th>
          <th>10-Student</th>
        </tr>
      </thead>
      <tbody>
        {programs.map((program) => (
          <tr key={program.program_id}>
            <td>{program.program_id}</td>
            <td>{program.program_name}</td>
            <td>
              <Badge bg="info">
                {program.total_enrollment} students
              </Badge>
            </td>
            <td>
              <Badge bg="primary">
                {program.blocks_20_count_fall} blocks
              </Badge>
            </td>
            <td>
              <Badge bg="secondary">
                {program.blocks_10_count_fall} blocks
              </Badge>
            </td>
            <td>
              <Badge bg="primary">
                {program.blocks_20_count_winter} blocks
              </Badge>
            </td>
            <td>
              <Badge bg="secondary">
                {program.blocks_10_count_winter} blocks
              </Badge>
            </td>
            <td>
              <Button
                variant="primary"
                size="sm"
                className="me-2"
                onClick={() => onEdit(program)}
              >
                Edit
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => onDelete(program.program_id)}
              >
                Delete
              </Button>
              <Button
                variant="info"
                size="sm"
                className="ms-2"
                onClick={() => onViewRequirements(program.program_id)}
              >
                Requirements
              </Button>
              <Button
                variant="success"
                size="sm"
                className="ms-2"
                onClick={() => onViewSchedules(program.program_id)}
              >
                View Schedules
              </Button>
            </td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};

export default ProgramsTable;
