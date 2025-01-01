import React, { useEffect, useState } from 'react';
import { Modal, Table, Button, Spinner } from 'react-bootstrap';

const BlockScheduleModal = ({ show, blockId, onHide }) => {
  const [schedule, setSchedule] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchSchedule = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/schedules/block/${blockId}`);
      if (response.ok) {
        const data = await response.json();
        setSchedule(data);
      } else {
        const error = await response.json();
        alert(error.error || 'Error fetching schedule');
      }
    } catch (error) {
      console.error('Error fetching schedule:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (show && blockId) {
      fetchSchedule();
    }
  }, [show, blockId]);

  const getDayName = (day) => {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[day - 1];
  };

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Block Schedule</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {isLoading ? (
          <div className="text-center p-4">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
          </div>
        ) : schedule.length === 0 ? (
          <div className="text-center p-4">No courses scheduled for this block</div>
        ) : (
          <Table striped bordered hover>
            <thead>
              <tr>
                <th>Course ID</th>
                <th>Section Type</th>
                <th>Section Code</th>
                <th>Day</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {schedule.map((offering) => (
                <tr key={offering.offering_id}>
                  <td>{offering.course_id}</td>
                  <td>{offering.section_type}</td>
                  <td>{offering.section_code}</td>
                  <td>{getDayName(offering.day_of_week)}</td>
                  <td>{`${offering.start_time}-${offering.end_time}`}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default BlockScheduleModal;
