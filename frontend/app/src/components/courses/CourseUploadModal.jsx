import React, { useState } from 'react';
import { Modal, Button, Table, Alert } from 'react-bootstrap';
import Papa from 'papaparse';

const CourseUploadModal = ({ show, onHide, onSave }) => {
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
          setParsedData(results.data);
          setError(null);
        }
      });
    }
  };

  const handleSave = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/courses/bulk', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ courses: parsedData })
      });

      if (response.ok) {
        onSave();
        onHide();
      } else {
        const error = await response.json();
        setError(error.message || 'Error uploading courses');
      }
    } catch (error) {
      setError('Error uploading courses');
    }
  };

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Upload Courses CSV</Modal.Title>
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
          <Table striped bordered hover>
            <thead>
              <tr>
                <th>Course ID</th>
                <th>Course Name</th>
                <th>Credits</th>
              </tr>
            </thead>
            <tbody>
              {parsedData.map((course, index) => (
                <tr key={index}>
                  <td>{course.course_id}</td>
                  <td>{course.course_name}</td>
                  <td>{course.credits}</td>
                </tr>
              ))}
            </tbody>
          </Table>
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
          Save Courses
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default CourseUploadModal;
