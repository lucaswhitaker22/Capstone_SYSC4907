import React, { useState, useEffect, useRef } from 'react';
import { Modal, Spinner, Button, ButtonGroup, Dropdown } from 'react-bootstrap';
import FullCalendar from '@fullcalendar/react';
import timeGridPlugin from '@fullcalendar/timegrid';
import bootstrap5Plugin from '@fullcalendar/bootstrap5';
import html2canvas from 'html2canvas';

const ScheduleViewModal = ({ show, blockId, onHide }) => {
  const [schedule, setSchedule] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const calendarRef = useRef(null);

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
// Export as PNG
const handleExportPNG = async () => {
  if (!calendarRef.current) return;
  
  const calendarEl = calendarRef.current.elRef.current;
  
  try {
    calendarEl.classList.add('export-view');
    
    const canvas = await html2canvas(calendarEl, {
      scale: 2,
      useCORS: true,
      logging: false,
      allowTaint: true
    });
    
    calendarEl.classList.remove('export-view');
    
    const image = canvas.toDataURL('image/png');
    const link = document.createElement('a');
    link.href = image;
    link.download = `schedule-block-${blockId}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error('Error generating PNG:', error);
    alert('Failed to export schedule as PNG');
  }
};

// Export as CSV
const handleExportCSV = () => {
  if (!schedule.length) return;
  
  // CSV header
  let csvContent = 'Course ID,Section Type,Section Code,Day,Start Time,End Time\n';
  
  // Fixed getDayName function to correctly map the day values
  const getDayName = (day) => {
    // Using the correct day mapping (days are stored as 1-7 where 1=Monday)
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    return days[(day - 1) % 7]; // Using modulo to handle out-of-bounds values
  };
  
  // Add data rows
  schedule.forEach(offering => {
    csvContent += `${offering.course_id},${offering.section_type},${offering.section_code},`;
    csvContent += `${getDayName(offering.day_of_week)},${offering.start_time},${offering.end_time}\n`;
  });
  
  // Create and trigger download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `schedule-block-${blockId}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
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
      daysOfWeek: [(offering.day_of_week % 7)], // Adjust if needed based on your day values
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
        <div>
          <div id="calendar-container">
            <FullCalendar
              ref={calendarRef}
              plugins={[timeGridPlugin, bootstrap5Plugin]}
              initialView="timeGridWeek"
              headerToolbar={false}
              allDaySlot={false}
              slotMinTime="08:00:00"
              slotMaxTime="22:00:00"
              weekends={true} // Changed to true to include Saturday and Sunday
              events={convertToCalendarEvents()}
              height="auto"
              themeSystem="bootstrap5"
            />
          </div>
          <div className="mt-3 d-flex justify-content-end">
            <ButtonGroup>
              <Button variant="primary" onClick={handleExportPNG}>Export as PNG</Button>
              <Button variant="secondary" onClick={handleExportCSV}>Export as CSV</Button>
            </ButtonGroup>
          </div>
        </div>
      )}
    </Modal.Body>
  </Modal>
);
};

export default ScheduleViewModal;