import React, { useState, useEffect } from 'react';
import { Container, Button } from 'react-bootstrap';
import OfferingsTable from './OfferingsTable';
import OfferingModal from './OfferingModal';

const API_URL = 'http://127.0.0.1:5000/api';

const OfferingsPage = () => {
  const [offerings, setOfferings] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedOffering, setSelectedOffering] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchOfferings = async () => {
    try {
      const response = await fetch(`${API_URL}/offerings`);
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
    </Container>
  );
};

export default OfferingsPage;

