import React, { useState, useEffect } from 'react';
import { Container, Button, Form } from 'react-bootstrap';
import ProgramsTable from './ProgramsTable';
import ProgramsModal from './ProgramsModal';
import ProgramRequirementsModal from './ProgramRequirementsModal';
import ExportPrograms from './ExportPrograms';

const API_URL = 'http://127.0.0.1:5000/api';

const ProgramsPage = () => {
  const [programs, setPrograms] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [showRequirementsModal, setShowRequirementsModal] = useState(false);
  const [selectedProgram, setSelectedProgram] = useState(null);
  const [selectedProgramId, setSelectedProgramId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentYear, setCurrentYear] = useState('2025-2026');

  const fetchPrograms = async () => {
      try {
          const params = new URLSearchParams({
              academic_year: currentYear
          });
          const response = await fetch(`${API_URL}/programs/?${params}`);
          const data = await response.json();
          setPrograms(data);
      } catch (error) {
          console.error('Error fetching programs:', error);
      } finally {
          setIsLoading(false);
      }
  };

  useEffect(() => {
      fetchPrograms();
  }, [currentYear]);


  const handleAddNew = () => {
    setSelectedProgram(null);
    setShowModal(true);
  };

  const handleEdit = (program) => {
    setSelectedProgram(program);
    setShowModal(true);
  };

  const handleDelete = async (programId) => {
    if (window.confirm('Are you sure you want to delete this program?')) {
      try {
        const response = await fetch(`${API_URL}/programs/${programId}`, {
          method: 'DELETE'
        });
        if (response.ok) {
          await fetchPrograms();
        } else {
          const error = await response.json();
          alert(error.error || 'Error deleting program');
        }
      } catch (error) {
        console.error('Error deleting program:', error);
      }
    }
  };

  const handleSave = async (formData) => {
    try {
      const method = selectedProgram ? 'PUT' : 'POST';
      const url = selectedProgram 
        ? `${API_URL}/programs/${selectedProgram.program_id}`
        : `${API_URL}/programs/`;

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setShowModal(false);
        await fetchPrograms();
      } else {
        const error = await response.json();
        alert(error.error || 'Error saving program');
      }
    } catch (error) {
      console.error('Error saving program:', error);
    }
  };

const handleViewRequirements = (programId) => {
    setSelectedProgramId(programId);
    setShowRequirementsModal(true);
  };


return (
  <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
          <h1>Program Management</h1>
          <div>
              <Form.Control
                  type="text"
                  className="me-2 d-inline-block"
                  style={{width: 'auto'}}
                  value={currentYear}
                  onChange={(e) => setCurrentYear(e.target.value)}
                  pattern="\d{4}-\d{4}"
                  placeholder="2025-2026"
              />
              <Button variant="primary" onClick={handleAddNew}>
                  Create New Program
              </Button>
              
          </div>
          <ExportPrograms 
            programs={programs}
            academicYear={currentYear}
            isLoading={isLoading}
          />
      </div>

      <ProgramsTable 
          programs={programs}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onViewRequirements={handleViewRequirements}
          isLoading={isLoading}
          academicYear={currentYear}
      />

      <ProgramsModal
          show={showModal}
          program={selectedProgram}
          onHide={() => setShowModal(false)}
          onSave={handleSave}
          academicYear={currentYear}
      />

      <ProgramRequirementsModal
          show={showRequirementsModal}
          programId={selectedProgramId}
          onHide={() => setShowRequirementsModal(false)}
          academicYear={currentYear}
      />
  </Container>
);
};

export default ProgramsPage;
