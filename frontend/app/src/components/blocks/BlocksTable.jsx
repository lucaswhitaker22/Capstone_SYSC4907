import React from 'react';
import { Table, Button, Badge, Spinner } from 'react-bootstrap';

const BlocksTable = ({ 
    blocks = [], 
    onEdit, 
    onDelete, 
    onViewSchedule, 
    onCalculateRating, 
    isLoading 
  }) => {
  if (isLoading) {
    return (
      <div className="text-center p-4">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
  }

  const getStatusBadge = (status) => {
    const variants = {
      'DRAFT': 'secondary',
      'PUBLISHED': 'success',
      'LOCKED': 'danger'
    };
    return (
      <Badge bg={variants[status] || 'secondary'}>
        {status}
      </Badge>
    );
  };

  const getValidationBadge = (block) => {
    if (!block.validation_status) return null;
    
    return (
      <Badge 
        bg={block.validation_status.is_valid ? 'success' : 'danger'}
        className="ms-2"
      >
        {block.validation_status.is_valid ? 'Valid' : 'Invalid'}
      </Badge>
    );
  };

  const getRatingColor = (rating) => {
    if (rating >= 80) return 'text-success';
    if (rating >= 60) return 'text-warning';
    return 'text-danger';
  };

  return (
    <Table striped bordered hover responsive>
      <thead>
        <tr>
          <th>Block ID</th>
          <th>Program ID</th>
          <th>Block Size</th>
          <th>Term</th>
          <th>Academic Year</th>
          <th>Schedule Rating</th>
          <th>Status</th>
          <th>Validation</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {blocks.map((block) => (
          <tr key={block.block_id}>
            <td>{block.block_id}</td>
            <td>{block.program_id}</td>
            <td>{block.block_size}</td>
            <td>{block.term}</td>
            <td>{block.academic_year}</td>
            <td className={getRatingColor(block.schedule_rating)}>
              {block.schedule_rating ? `${block.schedule_rating.toFixed(1)}%` : 'N/A'}
            </td>
            <td>
              {getStatusBadge(block.status)}
              {getValidationBadge(block)}
            </td>
            <td>
              {block.validation_status?.missing_requirements?.length > 0 && (
                <div className="text-danger small">
                  Missing courses: {block.validation_status.missing_requirements.map(r => r.course_id).join(', ')}
                </div>
              )}
            </td>
            <td>
              <Button
                variant="primary"
                size="sm"
                className="me-2"
                onClick={() => onEdit(block)}
                disabled={block.status === 'LOCKED'}
              >
                Edit
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => onDelete(block.block_id)}
                disabled={block.status === 'LOCKED'}
              >
                Delete
              </Button>
              <Button
                variant="info"
                size="sm"
                className="ms-2"
                onClick={() => onViewSchedule(block.block_id)}
              >
                View Schedule
              </Button>
              {block.status !== 'LOCKED' && (
                <Button
                  variant="success"
                  size="sm"
                  className="ms-2"
                  onClick={() => onCalculateRating(block.block_id)}
                >
                  Calculate Rating
                </Button>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};

export default BlocksTable;
