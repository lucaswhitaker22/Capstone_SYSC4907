import React, { useState, useEffect } from 'react';
import { Container, Button } from 'react-bootstrap';
import OfferingsTable from './OfferingsTable';
import OfferingModal from './OfferingModal';
import OfferingUploadModal from './OfferingUploadModal';
import Papa from 'papaparse';

const API_URL = 'http://127.0.0.1:5000/api';

const OfferingsPage = () => {
  const [offerings, setOfferings] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedOffering, setSelectedOffering] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const fetchOfferings = async () => {
    try {
      // Add default term and year to the request
      const params = new URLSearchParams({
        term: '',  // Default term
        academic_year: ''  // Default year
      });
      const response = await fetch(`${API_URL}/offerings?${params}`);
      const data = await response.json();
      setOfferings(data);
    } catch (error) {
      console.error('Error fetching offerings:', error);
    } finally {
      setIsLoading(false);
    }
};

  useEffect(() => {
    fetchOfferings();
  }, []);

  const handleAddNew = () => {
    setSelectedOffering(null);
    setShowModal(true);
  };
  const handleExportCSV = () => {
    const csvData = offerings.map(offering => ({
        course_id: offering.course_id,
        section_type: offering.section_type,
        section_code: offering.section_code,
        day_of_week: offering.day_of_week,
        start_time: offering.start_time,
        end_time: offering.end_time,
        capacity: offering.capacity,
        term: offering.term,
        academic_year: offering.academic_year,
        status: offering.status
    }));
    
    const csv = Papa.unparse(csvData, {
        header: true,
        delimiter: ","
    });
    
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `course-offerings-${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    URL.revokeObjectURL(url);
    document.body.removeChild(link);
};

  const handleEdit = (offering) => {
    setSelectedOffering(offering);
    setShowModal(true);
  };

  const handleDelete = async (offeringId) => {
    if (window.confirm('Are you sure you want to delete this offering?')) {
      try {
        const response = await fetch(`${API_URL}/offerings/${offeringId}`, {
          method: 'DELETE'
        });
        if (response.ok) {
          await fetchOfferings();
        } else {
          const error = await response.json();
          alert(error.error || 'Error deleting offering');
        }
      } catch (error) {
        console.error('Error deleting offering:', error);
      }
    }
  };

  const handleSave = async (formData) => {
    try {
      const method = selectedOffering ? 'PUT' : 'POST';
      const url = selectedOffering 
        ? `${API_URL}/offerings/${selectedOffering.offering_id}`
        : `${API_URL}/offerings`;

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setShowModal(false);
        await fetchOfferings();
      } else {
        const error = await response.json();
        alert(error.error || 'Error saving offering');
      }
    } catch (error) {
      console.error('Error saving offering:', error);
    }
  };

  return (
    <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Course Offerings</h1>

        <Button 
          variant="outline-primary" 
          className="me-2" 
          onClick={() => setShowUploadModal(true)}
        >
          Upload CSV
        </Button>
        <Button variant="success" className="me-2" onClick={handleExportCSV}>
            Export CSV
        </Button>
        <Button variant="primary" onClick={handleAddNew}>
          Add New Offering
        </Button>

      </div>

      <OfferingsTable 
        offerings={offerings}
        onEdit={handleEdit}
        onDelete={handleDelete}
        isLoading={isLoading}
      />

      <OfferingModal
        show={showModal}
        offering={selectedOffering}
        onHide={() => setShowModal(false)}
        onSave={handleSave}
      />
          <OfferingUploadModal
      show={showUploadModal}
      onHide={() => setShowUploadModal(false)}
      onSave={fetchOfferings}
    />
    </Container>
  );
};

export default OfferingsPage;

