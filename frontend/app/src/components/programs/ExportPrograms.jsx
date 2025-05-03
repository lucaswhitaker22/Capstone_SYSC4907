// frontend/app/src/components/programs/ExportPrograms.jsx
import React, { useState } from 'react';
import { Button, Spinner } from 'react-bootstrap';
import Papa from 'papaparse';

const API_URL = 'http://127.0.0.1:5000/api';

const ExportPrograms = ({ programs, academicYear, isLoading }) => {
  const [isExporting, setIsExporting] = useState(false);

  const fetchRequirementsForProgram = async (programId) => {
    try {
      const response = await fetch(`${API_URL}/requirements/program/${programId}`);
      if (response.ok) {
        return await response.json();
      }
      return [];
    } catch (error) {
      console.error(`Error fetching requirements for program ${programId}:`, error);
      return [];
    }
  };

  const exportToCSV = async () => {
    if (programs.length === 0) {
      alert('No programs to export');
      return;
    }

    setIsExporting(true);

    try {
      // First, create the basic program data
      const programData = programs.map(program => ({
        program_id: program.program_id,
        program_name: program.program_name,
        total_enrollment: program.total_enrollment || 0,
        blocks_20_count_fall: program.blocks_20_count_fall || 0,
        blocks_10_count_fall: program.blocks_10_count_fall || 0,
        blocks_20_count_winter: program.blocks_20_count_winter || 0,
        blocks_10_count_winter: program.blocks_10_count_winter || 0,
        academic_year: program.academic_year,
        requirements: [] // Will be filled with requirements data
      }));

      // Fetch requirements for each program
      for (let i = 0; i < programData.length; i++) {
        const requirements = await fetchRequirementsForProgram(programData[i].program_id);
        programData[i].requirements = requirements.map(req => req.course_id).join(', ');
      }

      // Convert to CSV using Papa Parse
      const csv = Papa.unparse({
        fields: [
          'Program ID', 
          'Program Name', 
          'Total Enrollment', 
          '20-Student Blocks (Fall)', 
          '10-Student Blocks (Fall)',
          '20-Student Blocks (Winter)',
          '10-Student Blocks (Winter)',
          'Academic Year',
          'Required Courses'
        ],
        data: programData.map(program => [
          program.program_id,
          program.program_name,
          program.total_enrollment,
          program.blocks_20_count_fall,
          program.blocks_10_count_fall,
          program.blocks_20_count_winter,
          program.blocks_10_count_winter,
          program.academic_year,
          program.requirements
        ])
      });
      
      // Create a download link and trigger the download
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `programs_with_requirements_${academicYear}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error exporting programs with requirements:', error);
      alert('Error exporting programs. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <Button 
      variant="success" 
      onClick={exportToCSV}
      disabled={isLoading || isExporting}
    >
      {isExporting ? (
        <>
          <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-2" />
          Exporting...
        </>
      ) : (
        'Export CSV'
      )}
    </Button>
  );
};

export default ExportPrograms;
