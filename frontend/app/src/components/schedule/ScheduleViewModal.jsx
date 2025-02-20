import React, { useState, useEffect } from 'react';
import { Modal, Spinner } from 'react-bootstrap';
import FullCalendar from '@fullcalendar/react';
import timeGridPlugin from '@fullcalendar/timegrid';
import bootstrap5Plugin from '@fullcalendar/bootstrap5';

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

  const getEventColor = (sectionType) => {
    const colors = {
      'LECTURE': '#007bff',
      'LAB': '#28a745',
      'TUTORIAL': '#ffc107'
    };
    return colors[sectionType] || '#6c757d';
  };

  const convertToCalendarEvents = () => {
    return schedule.map(offering => {
      const [hours, minutes] = offering.start_time.split(':');
      const [endHours, endMinutes] = offering.end_time.split(':');
      
      return {
        id: offering.offering_id,
        title: `${offering.course_id} - ${offering.section_type}`,
        daysOfWeek: [offering.day_of_week - 1],
        startTime: `${hours}:${minutes}:00`,
        endTime: `${endHours}:${endMinutes}:00`,
        backgroundColor: getEventColor(offering.section_type),
        extendedProps: {
          sectionCode: offering.section_code,
          courseId: offering.course_id,
          sectionType: offering.section_type
        }
      };
    });
  };

  return (
    <Modal show={show} onHide={onHide} size="xl" dialogClassName="modal-90w">
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
          <div style={{ height: '600px' }}>
            <FullCalendar
              plugins={[timeGridPlugin, bootstrap5Plugin]}
              initialView="timeGridWeek"
              themeSystem="bootstrap5"
              headerToolbar={false}
              allDaySlot={false}
              slotMinTime="08:00:00"
              slotMaxTime="22:00:00"
              events={convertToCalendarEvents()}
              eventContent={renderEventContent}
              slotDuration="00:30:00"
              weekends={false}
              dayHeaderFormat={{ weekday: 'long' }}
              height="100%"
            />
          </div>
        )}
      </Modal.Body>
    </Modal>
  );
};

const renderEventContent = (eventInfo) => {
  return (
    <div className="p-1">
      <div className="fw-bold">{eventInfo.event.extendedProps.courseId}</div>
      <div className="small">{eventInfo.event.extendedProps.sectionType}</div>
      <div className="small">{eventInfo.event.extendedProps.sectionCode}</div>
    </div>
  );
};

export default ScheduleViewModal;
