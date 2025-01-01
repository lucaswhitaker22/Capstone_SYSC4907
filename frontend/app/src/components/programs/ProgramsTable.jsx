import React from 'react';
import { Table, Button, Badge, Spinner } from 'react-bootstrap';

const ProgramsTable = ({ programs = [], onEdit, onDelete, isLoading, onViewRequirements }) => {
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
          <th>Program ID</th>
          <th>Program Name</th>
          <th>Total Enrollment</th>
          <th>20-Student Blocks</th>
          <th>10-Student Blocks</th>
          <th>Actions</th>
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
                {program.blocks_20_count} blocks
              </Badge>
            </td>
            <td>
              <Badge bg="secondary">
                {program.blocks_10_count} blocks
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
                disabled={program.total_enrollment > 0}
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
            </td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};

export default ProgramsTable;
