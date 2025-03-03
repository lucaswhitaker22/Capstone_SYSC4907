import React from 'react';
import { Table, Button, Badge, Spinner } from 'react-bootstrap';

const ProgramsTable = ({ programs = [], onEdit, onDelete, isLoading, onViewRequirements }) => {
  if (isLoading) {
    return (
      <div className="text-center p-3">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
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
            <td>{program.total_enrollment}</td>
            <td>{program.blocks_20_count}</td>
            <td>{program.blocks_10_count}</td>
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
                className="me-2"
                onClick={() => onDelete(program.program_id)}
              >
                Delete
              </Button>
              <Button
                variant="info"
                size="sm"
                className="me-2"
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
