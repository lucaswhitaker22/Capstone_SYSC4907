import React, { useState } from 'react';
import { Modal, Button, Table, Alert } from 'react-bootstrap';
import Papa from 'papaparse';

const OfferingUploadModal = ({ show, onHide, onSave }) => {
  const [parsedData, setParsedData] = useState([]);
  const [error, setError] = useState(null);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        complete: (results) => {
          if (results.errors.length > 0) {
            setError('Error parsing CSV file');
            return;
          }
          // Convert string values to appropriate types
          const formattedData = results.data.map(row => ({
            ...row,
            offering_id: parseInt(row.offering_id),
            day_of_week: parseInt(row.day_of_week),
            capacity: parseInt(row.capacity),
            current_enrollment: parseInt(row.current_enrollment)
          }));
          setParsedData(formattedData);
          setError(null);
        }
      });
    }
  };

  const handleSave = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/offerings/bulk', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ offerings: parsedData })
      });

      if (response.ok) {
        onSave();
        onHide();
      } else {
        const error = await response.json();
        setError(error.message || 'Error uploading offerings');
      }
    } catch (error) {
      setError('Error uploading offerings');
    }
  };

  const getDayName = (day) => {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[day - 1];
  };

  return (
    <Modal show={show} onHide={onHide} size="xl">
      <Modal.Header closeButton>
        <Modal.Title>Upload Course Offerings CSV</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <div className="mb-3">
          <input
            type="file"
            accept=".csv"
            onChange={handleFileUpload}
            className="form-control"
          />
        </div>

        {error && (
          <Alert variant="danger" className="mb-3">
            {error}
          </Alert>
        )}

        {parsedData.length > 0 && (
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            <Table striped bordered hover>
              <thead>
                <tr>
                  <th>Course ID</th>
                  <th>Section Type</th>
                  <th>Section Code</th>
                  <th>Day</th>
                  <th>Time</th>
                  <th>Capacity</th>
                  <th>Term</th>
                  <th>Academic Year</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {parsedData.map((offering, index) => (
                  <tr key={index}>
                    <td>{offering.course_id}</td>
                    <td>{offering.section_type}</td>
                    <td>{offering.section_code}</td>
                    <td>{getDayName(offering.day_of_week)}</td>
                    <td>{`${offering.start_time} - ${offering.end_time}`}</td>
                    <td>{offering.capacity}</td>
                    <td>{offering.term}</td>
                    <td>{offering.academic_year}</td>
                    <td>{offering.status}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </div>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={handleSave}
          disabled={parsedData.length === 0}
        >
          Save Offerings
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default OfferingUploadModal;
