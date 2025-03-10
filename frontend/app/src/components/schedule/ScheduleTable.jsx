import React, { useState, useEffect } from 'react';
import { Table, Button, Badge, Spinner, Form, Card, Collapse, Row, Col } from 'react-bootstrap';

const ScheduleTable = ({
  schedules = [],
  onView,
  onEdit,
  onValidate,
  onDelete,
  isLoading,
  onGenerate,
  onSelectionChange,
  selectedBlocks,
  onStatusUpdate,
  onSort
}) => {
  const [selectedRows, setSelectedRows] = useState([]);
  const [sortOrder, setSortOrder] = useState('desc');
  const [filters, setFilters] = useState({
    block_id: '',
    program_id: [],
    courses: [],
    days: '',
    rating: { min: 0, max: 100 }
  });
  const [showFilters, setShowFilters] = useState(false);
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
  const handleSort = () => {
    const newSortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
    setSortOrder(newSortOrder);
    onSort(newSortOrder);
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };
  const applyFilters = (schedule) => {
    const ratingPercentage = schedule.rating ? (schedule.rating / 2).toFixed(1) : null;
    return (
      (filters.block_id === '' || schedule.block_id.toString().includes(filters.block_id)) &&
      (filters.program_id.length === 0 || filters.program_id.includes(schedule.program_id)) &&
      (filters.courses.length === 0 || schedule.offerings.some(o => filters.courses.includes(o.course_id))) &&
      (ratingPercentage >= filters.rating.min && ratingPercentage <= filters.rating.max)
    );
  };

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
  const StatusDropdown = ({ blockId, currentStatus, onStatusUpdate }) => {
    const [isOpen, setIsOpen] = useState(false);
    
    const statuses = [
      { value: 'DRAFT', label: 'Draft', variant: 'secondary' },
      { value: 'PUBLISHED', label: 'Published', variant: 'success' },
      { value: 'LOCKED', label: 'Locked', variant: 'warning' },
      { value: 'ARCHIVED', label: 'Archived', variant: 'dark' }
    ];
    
    const handleStatusSelect = (status) => {
      if (status !== currentStatus) {
        onStatusUpdate(blockId, status);
      }
      setIsOpen(false);
    };

    return (
      <div className="position-relative">
        <Badge 
          bg={statuses.find(s => s.value === currentStatus)?.variant || 'secondary'} 
          style={{ cursor: 'pointer' }}
          onClick={() => setIsOpen(!isOpen)}
        >
          {statuses.find(s => s.value === currentStatus)?.label || 'Draft'} ▼
        </Badge>
        
        {isOpen && (
          <div className="status-dropdown" style={{
            position: 'absolute',
            zIndex: 1000,
            backgroundColor: 'white',
            border: '1px solid #dee2e6',
            borderRadius: '0.25rem',
            padding: '0.5rem 0',
            minWidth: '120px'
          }}>
            {statuses.map(status => (
              <div 
                key={status.value}
                onClick={() => handleStatusSelect(status.value)}
                style={{
                  padding: '0.25rem 1rem',
                  cursor: 'pointer',
                  backgroundColor: status.value === currentStatus ? '#f8f9fa' : 'transparent'
                }}
              >
                <Badge bg={status.variant}>{status.label}</Badge>
              </div>
            ))}
          </div>
        )}
      </div>
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
  const getStatusBadge = (status) => {
    switch (status) {
      case 'DRAFT':
        return <Badge bg="secondary">Draft</Badge>;
      case 'PUBLISHED':
        return <Badge bg="success">Published</Badge>;
      case 'LOCKED':
        return <Badge bg="warning">Locked</Badge>;
      case 'ARCHIVED':
        return <Badge bg="dark">Archived</Badge>;
      default:
        return <Badge bg="light" text="dark">Unknown</Badge>;
    }
  };
  const isGenerateEnabled = (status) => {
    return status === 'DRAFT';
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
              <Form.Label>Block ID</Form.Label>
              <Form.Control
                type="text"
                value={filters.block_id}
                onChange={(e) => handleFilterChange('block_id', e.target.value)}
              />
            </Form.Group>
          </Col>
          <Col md={3}>
            <Form.Group>
              <Form.Label>Program</Form.Label>
              <Form.Select
                multiple
                value={filters.program_id}
                onChange={(e) => handleFilterChange('program_id', Array.from(e.target.selectedOptions, option => option.value))}
              >
                {[...new Set(schedules.map(s => s.program_id))].map(program => (
                  <option key={program} value={program}>{program}</option>
                ))}
              </Form.Select>
            </Form.Group>
          </Col>
          <Col md={3}>
            <Form.Group>
              <Form.Label>Courses</Form.Label>
              <Form.Select
                multiple
                value={filters.courses}
                onChange={(e) => handleFilterChange('courses', Array.from(e.target.selectedOptions, option => option.value))}
              >
                {[...new Set(schedules.flatMap(s => s.offerings.map(o => o.course_id)))].map(course => (
                  <option key={course} value={course}>{course}</option>
                ))}
              </Form.Select>
            </Form.Group>
          </Col>

        </Row>
        <Row className="mt-3">
          <Col md={6}>
            <Form.Group>
              <Form.Label>Rating Range (Min-Max)</Form.Label>
              <div className="d-flex align-items-center">
                <Form.Range
                  min={0}
                  max={100}
                  step={5}
                  value={filters.rating.min}
                  onChange={(e) => handleFilterChange('rating', { ...filters.rating, min: parseInt(e.target.value) })}
                />
                <span className="ms-2">{filters.rating.min}</span>
              </div>
              <div className="d-flex align-items-center">
                <Form.Range
                  min={0}
                  max={100}
                  step={5}
                  value={filters.rating.max}
                  onChange={(e) => handleFilterChange('rating', { ...filters.rating, max: parseInt(e.target.value) })}
                />
                <span className="ms-2">{filters.rating.max}</span>
              </div>
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
          <th>
          <input
  type="checkbox"
  onChange={handleSelectAll}
  checked={selectedRows.length === schedules.length}
/>
          </th>
          <th>Block ID</th>
          <th>Program</th>
          <th>Courses</th>
          <th>Days</th>
          <th>Status</th>
          <th onClick={handleSort} style={{ cursor: 'pointer' }}>
            Rating {sortOrder === 'asc' ? '▲' : '▼'}
          </th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
   {schedules.filter(applyFilters).map((schedule) => (
    <tr key={schedule.block_id}>
                <td>
              <input
                type="checkbox"
                onChange={() => handleRowSelection(schedule.block_id)}
                checked={selectedBlocks.includes(schedule.block_id)} // Use selectedBlocks prop
              />
            </td>
            <td>Block {schedule.block_id}</td>
            <td>{schedule.program_id}</td>
            <td>
              <Badge bg="info">
                {getCoursesCount(schedule.offerings)} courses
              </Badge>
            </td>
            <td>{getDaysString(schedule.offerings)}</td>
            <td>
            {onStatusUpdate ? (
                  <StatusDropdown
                  blockId={schedule.block_id}
                  currentStatus={schedule.status}
                    onStatusUpdate={onStatusUpdate}
                  />
                ) : (
                  getStatusBadge(schedule.status)
                )}
            </td>
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
                variant="primary"
                size="sm"
                onClick={() => onGenerate(schedule.block_id)}
                disabled={!isGenerateEnabled(schedule.status)}
                title={!isGenerateEnabled(schedule.status) ? 
                  'Schedule can only be generated when in Draft status' : 
                  'Generate schedule'}
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
    </>
  );
};

export default ScheduleTable;