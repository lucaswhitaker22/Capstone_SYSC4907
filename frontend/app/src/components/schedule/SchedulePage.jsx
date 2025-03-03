import React, { useState, useEffect } from 'react';
import { Container, Button, Form, Tab, Tabs} from 'react-bootstrap';
import ScheduleTable from './ScheduleTable';
import ScheduleViewModal from './ScheduleViewModal';
import ScheduleEditModal from './ScheduleEditModal';
import { Bars } from 'react-loading-icons';

const API_URL = 'http://127.0.0.1:5000/api';

const SchedulePage = () => {
    const [schedules, setSchedules] = useState([]);
    const [blocks, setBlocks] = useState([]);
    const [offerings, setOfferings] = useState([]);
    const [selectedBlock, setSelectedBlock] = useState(null);
    const [selectedTerm, setSelectedTerm] = useState('FALL');
    const [selectedYear, setSelectedYear] = useState('2025-2026');
    const [showViewModal, setShowViewModal] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [showGenerateModal, setShowGenerateModal] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [selectedFallBlocks, setSelectedFallBlocks] = useState([]);
    const [selectedWinterBlocks, setSelectedWinterBlocks] = useState([]);
    const [isBulkGenerating, setIsBulkGenerating] = useState(false);
    const [isBulkClearing, setIsBulkClearing] = useState(false);
    const [activeTab, setActiveTab] = useState('FALL');

    const fetchBlocks = async () => {
        try {
            const response = await fetch(`${API_URL}/blocks`);
            const data = await response.json();
            setBlocks(data);
        } catch (error) {
            console.error('Error fetching blocks:', error);
        }
    };

    const fetchOfferings = async () => {
        try {
            const response = await fetch(`${API_URL}/offerings`);
            const data = await response.json();
            setOfferings(data);
        } catch (error) {
            console.error('Error fetching offerings:', error);
        }
    };

    const fetchBlockSchedule = async (blockId) => {
        try {
            const [scheduleResponse, validationResponse, ratingResponse] = await Promise.all([
                fetch(`${API_URL}/schedules/block/${blockId}`),
                fetch(`${API_URL}/schedules/block/${blockId}/validate`),
                fetch(`${API_URL}/schedules/block/${blockId}/rate`)
            ]);
    
            const offerings = await scheduleResponse.json();
            const validation = await validationResponse.json();
            const rating = await ratingResponse.json();
    
            return {
                offerings: scheduleResponse.ok ? offerings : [],
                validation: validationResponse.ok ? validation : null,
                rating: ratingResponse.ok ? rating.rating : null
            };
        } catch (error) {
            console.error('Error fetching block schedule:', error);
            return { offerings: [], validation: null, rating: null };
        }
    };
    

    const fetchAllSchedules = async () => {
        setIsLoading(true);
        try {
          const schedulesData = await Promise.all(
            blocks.filter(block => block.term === 'FALL' || block.term === 'WINTER').map(async (block) => {
              const { offerings, validation } = await fetchBlockSchedule(block.block_id);
              return {
                block_id: block.block_id,
                program_id: block.program_id,
                term: block.term,
                academic_year: block.academic_year,
                offerings: offerings,
                rating: block.schedule_rating,
                validation: validation
              };
            })
          );
          setSchedules(schedulesData);
        } catch (error) {
          console.error('Error fetching schedules:', error);
        } finally {
          setIsLoading(false);
        }
      };

    useEffect(() => {
        fetchBlocks();
        fetchOfferings();
    }, [selectedTerm]);

    useEffect(() => {
        if (blocks.length > 0) {
            fetchAllSchedules();
        }
    }, [blocks, selectedTerm]);

    const handleViewSchedule = (blockId) => {
        setSelectedBlock(blockId);
        setShowViewModal(true);
    };

    const handleEditSchedule = (blockId) => {
        setSelectedBlock(blockId);
        setShowEditModal(true);
    };

    

    const handleGenerateSchedule = async (blockId) => {
        try {
            const response = await fetch(`${API_URL}/schedules/block/${blockId}/generate`, {
                method: 'POST'
            });
            
            if (response.ok) {
                const generatedData = await response.json();
                
                // Update the specific block's rating in the blocks array
                setBlocks(prevBlocks => 
                    prevBlocks.map(block => 
                        block.block_id === blockId 
                            ? { ...block, schedule_rating: generatedData.schedule_rating }
                            : block
                    )
                );
                
                // Fetch updated schedules to reflect new changes
                await fetchAllSchedules();
            } else {
                const error = await response.json();
                alert(error.error || 'Error generating schedule');
            }
        } catch (error) {
            console.error('Error generating schedule:', error);
            alert('Error generating schedule');
        }
    };
    

    const handleDeleteSchedule = async (blockId) => {
        if (window.confirm('Are you sure you want to delete this schedule?')) {
            try {
                const response = await fetch(`${API_URL}/schedules/block/${blockId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    // Update the blocks array to reset the rating to 0
                    setBlocks(prevBlocks =>
                        prevBlocks.map(block =>
                            block.block_id === blockId
                                ? { ...block, schedule_rating: 0 }
                                : block
                        )
                    );
                    
                    // Update the schedules array
                    setSchedules(prevSchedules =>
                        prevSchedules.map(schedule =>
                            schedule.block_id === blockId
                                ? { ...schedule, rating: 0, offerings: [] }
                                : schedule
                        )
                    );
                    
                    // Fetch updated schedules to reflect new changes
                    await fetchAllSchedules();
                } else {
                    const error = await response.json();
                    alert(error.error || 'Error deleting schedule');
                }
            } catch (error) {
                console.error('Error deleting schedule:', error);
                alert('Error deleting schedule');
            }
        }
    };
    
    const handleSelectionChange = (selectedRows) => {
        if (activeTab === 'FALL') {
          setSelectedFallBlocks(selectedRows);
        } else {
          setSelectedWinterBlocks(selectedRows);
        }
      };
    
      const handleBulkGenerate = async () => {
      };
      
      const handleBulkClear = async () => {
      };

    const handleValidateSchedule = async (blockId) => {
        try {
            const response = await fetch(`${API_URL}/schedules/block/${blockId}/validate`);
            if (response.ok) {
                const data = await response.json();
                if (!data.is_valid) {
                    const missingCourses = data.missing_requirements
                        .map(r => r.course_id)
                        .join(', ');
                    alert(`Schedule validation failed.\nMissing courses: ${missingCourses}`);
                } else {
                    alert('Schedule is valid!');
                }
                return data;
            }
        } catch (error) {
            console.error('Error validating schedule:', error);
            alert('Error validating schedule');
        }
    };

    return (
        <Container className="py-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h1>Block Schedules</h1>
                <div className="d-flex gap-3">
                    <Form.Select 
                        value={selectedYear}
                        onChange={(e) => setSelectedYear(e.target.value)}
                        style={{ width: '150px' }}
                    >
                        <option value="2024-2025">2024-2025</option>
                        <option value="2025-2026">2025-2026</option>
                        <option value="2026-2027">2026-2027</option>
                    </Form.Select>
                </div>
            </div>
            <Tabs
  activeKey={activeTab}
  onSelect={(k) => setActiveTab(k)}
  className="mb-3"
>
  <Tab eventKey="FALL" title="Fall">
    <ScheduleTable
      schedules={schedules.filter(s => s.term === 'FALL')}
      onView={handleViewSchedule}
      onEdit={handleEditSchedule}
      onValidate={handleValidateSchedule}
      onDelete={handleDeleteSchedule}
      isLoading={isLoading}
      onGenerate={handleGenerateSchedule}
      onSelectionChange={handleSelectionChange}
    />
  </Tab>
  <Tab eventKey="WINTER" title="Winter">
    <ScheduleTable
      schedules={schedules.filter(s => s.term === 'WINTER')}
      onView={handleViewSchedule}
      onEdit={handleEditSchedule}
      onValidate={handleValidateSchedule}
      onDelete={handleDeleteSchedule}
      isLoading={isLoading}
      onGenerate={handleGenerateSchedule}
      onSelectionChange={handleSelectionChange}
    />
  </Tab>
</Tabs>
<div className="mt-3 d-flex align-items-center">
  <span className="me-3">Selected: {selectedFallBlocks.length + selectedWinterBlocks.length}</span>
  <Button 
    onClick={handleBulkGenerate} 
    disabled={(selectedFallBlocks.length + selectedWinterBlocks.length) === 0 || isBulkGenerating}
  >
    {isBulkGenerating ? (
      <>
        <Bars height="1em" stroke="#ffffff" style={{marginRight: '0.5em'}} />
        Generating...
      </>
    ) : (
      'Bulk Generate'
    )}
  </Button>
  <Button 
    onClick={handleBulkClear} 
    disabled={(selectedFallBlocks.length + selectedWinterBlocks.length) === 0 || isBulkClearing}
    className="ms-2"
  >
    {isBulkClearing ? (
      <>
        <Bars height="1em" stroke="#ffffff" style={{marginRight: '0.5em'}} />
        Clearing...
      </>
    ) : (
      'Bulk Clear'
    )}
  </Button>
</div>
            <ScheduleViewModal
                show={showViewModal}
                blockId={selectedBlock}
                term={selectedTerm}
                academicYear={selectedYear}
                onHide={() => setShowViewModal(false)}
            />

            <ScheduleEditModal
                show={showEditModal}
                blockId={selectedBlock}
                term={selectedTerm}
                academicYear={selectedYear}
                offerings={offerings}
                onHide={() => setShowEditModal(false)}
                onSave={fetchAllSchedules}
            />
        </Container>
    );
};
export default SchedulePage;
