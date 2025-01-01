import React, { useState } from 'react';
import { Container, Button, Row, Col, Card } from 'react-bootstrap';
import OfferingConflictModal from './OfferingConflictModal';
import ScheduleConflictModal from './ScheduleConflictModal';
import CourseConflictModal from './CourseConflictModal';

const ConflictsPage = () => {
  const [activeModal, setActiveModal] = useState(null);

  const conflictTypes = [
    {
      id: 'offering',
      title: 'Offering Conflicts',
      description: 'Check for time conflicts between two course offerings.',
      buttonText: 'Check Offering Conflicts'
    },
    {
      id: 'schedule',
      title: 'Schedule Conflicts',
      description: 'Check for conflicts in a set of course offerings.',
      buttonText: 'Check Schedule Conflicts'
    },
    {
      id: 'course',
      title: 'Course Conflicts',
      description: 'Check if a new course conflicts with existing schedule.',
      buttonText: 'Check Course Conflicts'
    }
  ];

  const renderConflictCard = ({ id, title, description, buttonText }) => (
    <Col md={4} key={id}>
      <Card className="h-100 mb-3">
        <Card.Body className="d-flex flex-column">
          <Card.Title>{title}</Card.Title>
          <Card.Text className="flex-grow-1">{description}</Card.Text>
          <Button 
            variant="primary" 
            onClick={() => setActiveModal(id)}
            className="mt-auto"
          >
            {buttonText}
          </Button>
        </Card.Body>
      </Card>
    </Col>
  );

  return (
    <Container className="py-4">
      <h1 className="mb-4">Conflict Checker</h1>
      
      <Row className="g-4">
        {conflictTypes.map(renderConflictCard)}
      </Row>

      <OfferingConflictModal 
        show={activeModal === 'offering'}
        onHide={() => setActiveModal(null)}
      />
      <ScheduleConflictModal
        show={activeModal === 'schedule'}
        onHide={() => setActiveModal(null)}
      />
      <CourseConflictModal
        show={activeModal === 'course'}
        onHide={() => setActiveModal(null)}
      />
    </Container>
  );
};

export default ConflictsPage;
