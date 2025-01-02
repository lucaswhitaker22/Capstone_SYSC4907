import React, { useState, useEffect } from 'react';
import { Container, Button } from 'react-bootstrap';
import ProgramsTable from './ProgramsTable';
import ProgramsModal from './ProgramsModal';
import ProgramRequirementsModal from './ProgramRequirementsModal';
import ProgramUploadModal from './ProgramUploadModal';
import Papa from 'papaparse';

const API_URL = 'http://127.0.0.1:5000/api';

const ProgramsPage = () => {
    const [programs, setPrograms] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [showRequirementsModal, setShowRequirementsModal] = useState(false);
    const [selectedProgram, setSelectedProgram] = useState(null);
    const [selectedProgramId, setSelectedProgramId] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [showUploadModal, setShowUploadModal] = useState(false);

  const fetchPrograms = async () => {
    try {
      const response = await fetch(`${API_URL}/programs/`);
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
  }, []);

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

// Add export function
const handleExportCSV = () => {
  const csv = Papa.unparse(programs.map(program => ({
      program_id: program.program_id,
      program_name: program.program_name,
      total_enrollment: program.total_enrollment,
      blocks_20_count: program.blocks_20_count,
      blocks_10_count: program.blocks_10_count
  })));
  
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.href = url;
  link.setAttribute('download', 'programs.csv');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

  return (
    <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Program Management</h1>
        <Button variant="secondary" className="me-2" onClick={() => setShowUploadModal(true)}>
            Upload CSV
        </Button>
        <Button variant="success" className="me-2" onClick={handleExportCSV}>
            Export CSV
        </Button>
        <Button variant="primary" onClick={handleAddNew}>
          Create New Program
        </Button>
      </div>

      <ProgramsTable 
        programs={programs}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onViewRequirements={handleViewRequirements}
        isLoading={isLoading}
      />

      <ProgramsModal
        show={showModal}
        program={selectedProgram}
        onHide={() => setShowModal(false)}
        onSave={handleSave}
      />

        <ProgramRequirementsModal
        show={showRequirementsModal}
        programId={selectedProgramId}
        onHide={() => setShowRequirementsModal(false)}
      />
      <ProgramUploadModal
    show={showUploadModal}
    onHide={() => setShowUploadModal(false)}
    onSave={fetchPrograms}
/>
    </Container>
  );
};

export default ProgramsPage;
