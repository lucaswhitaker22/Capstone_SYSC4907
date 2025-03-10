// frontend/app/src/components/schedule/ExportCSVButton.jsx
import React from 'react';
import { Button } from 'react-bootstrap';

const ExportSchedule = ({ schedules, activeTab, selectedYear, isLoading }) => {
  const exportToCSV = () => {
    // Get the current tab's schedules
    const currentTabSchedules = schedules.filter(schedule => schedule.term === activeTab);
    
    if (currentTabSchedules.length === 0) {
      alert('No schedules to export');
      return;
    }
    
    // CSV header
    let csvContent = 'Block ID,Program ID,Term,Academic Year,Course ID,Section Type,Section Code,Day,Time,Rating\n';
    
    // Helper function to get day name
    const getDayName = (day) => {
      const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
      return days[day - 1];
    };
    
    // Add rows for each schedule offering
    currentTabSchedules.forEach(schedule => {
      // If no offerings, add a single row with just the block info
      if (!schedule.offerings || schedule.offerings.length === 0) {
        csvContent += `${schedule.block_id},${schedule.program_id},${schedule.term},${schedule.academic_year},,,,,,${schedule.rating || 0}\n`;
      } else {
        // Add a row for each offering in the schedule
        schedule.offerings.forEach(offering => {
          csvContent += `${schedule.block_id},${schedule.program_id},${schedule.term},${schedule.academic_year},`;
          csvContent += `${offering.course_id},${offering.section_type},${offering.section_code},`;
          csvContent += `${getDayName(offering.day_of_week)},${offering.start_time}-${offering.end_time},${schedule.rating || 0}\n`;
        });
      }
    });
    
    // Create a download link and trigger the download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `${activeTab}_schedules_${selectedYear}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Button 
      variant="success" 
      onClick={exportToCSV}
      disabled={isLoading}
    >
      Export CSV
    </Button>
  );
};

export default ExportSchedule;
