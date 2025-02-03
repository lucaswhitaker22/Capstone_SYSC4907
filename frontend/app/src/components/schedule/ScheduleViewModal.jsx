import React, { useState, useEffect } from 'react';
import { Modal, Table, Badge, Spinner } from 'react-bootstrap';

const ScheduleViewModal = ({ show, blockId, onHide }) => {
  const [schedule, setSchedule] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (show && blockId) {
      fetchSchedule();
    }
  }, [show, blockId]);

  const fetchSchedule = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/schedules/block/${blockId}`);
      if (response.ok) {
        const data = await response.json();
        setSchedule(data);
      }
    } catch (error) {
      console.error('Error fetching schedule:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getDayName = (day) => {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[day];
  };

  const renderTimeSlot = (offering) => {
    return (
      <div className="p-2 border rounded mb-2" key={offering.offering_id}>
        <Badge bg="primary" className="me-2">{offering.section_type}</Badge>
        <strong>{offering.course_id}</strong> - {offering.section_code}
        <br />
        <small>{offering.start_time} - {offering.end_time}</small>
      </div>
    );
  };

  const renderScheduleTable = () => {
    const days = [1, 2, 3, 4, 5]; // Monday to Friday
    const scheduleByDay = days.map(day => ({
      day,
      offerings: schedule.filter(offering => offering.day_of_week === day)
    }));

    return (
      <Table bordered responsive>
        <thead>
          <tr>
            {days.map(day => (
              <th key={day} className="text-center">{getDayName(day)}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            {scheduleByDay.map(({ day, offerings }) => (
              <td key={day} className="align-top" style={{ minWidth: '200px' }}>
                {offerings.sort((a, b) => a.start_time.localeCompare(b.start_time))
                  .map(offering => renderTimeSlot(offering))}
              </td>
            ))}
          </tr>
        </tbody>
      </Table>
    );
  };

  return (
    <Modal show={show} onHide={onHide} size="xl">
      <Modal.Header closeButton>
        <Modal.Title>Block Schedule View</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {isLoading ? (
          <div className="text-center p-4">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading schedule...</span>
            </Spinner>
          </div>
        ) : schedule.length === 0 ? (
          <div className="text-center p-4">No courses scheduled for this block</div>
        ) : (
          renderScheduleTable()
        )}
      </Modal.Body>
    </Modal>
  );
};

export default ScheduleViewModal;
