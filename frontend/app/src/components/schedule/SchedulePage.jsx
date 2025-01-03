import React, { useState, useEffect } from 'react';
import { Container, Button } from 'react-bootstrap';
import ScheduleTable from './ScheduleTable';
import ScheduleViewModal from './ScheduleViewModal';
import ScheduleEditModal from './ScheduleEditModal';
import ScheduleGenerateModal from './ScheduleGenerateModal';

const API_URL = 'http://127.0.0.1:5000/api';

const SchedulePage = () => {
    const [schedules, setSchedules] = useState([]);
    const [blocks, setBlocks] = useState([]);
    const [offerings, setOfferings] = useState([]);
    const [selectedBlock, setSelectedBlock] = useState(null);
    const [showViewModal, setShowViewModal] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [showGenerateModal, setShowGenerateModal] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

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
            const [scheduleResponse, validationResponse] = await Promise.all([
                fetch(`${API_URL}/schedules/block/${blockId}`),
                fetch(`${API_URL}/schedules/block/${blockId}/validate`)
            ]);

            const offerings = await scheduleResponse.json();
            const validation = await validationResponse.json();

            return {
                offerings: scheduleResponse.ok ? offerings : [],
                validation: validationResponse.ok ? validation : null
            };
        } catch (error) {
            console.error('Error fetching block schedule:', error);
            return { offerings: [], validation: null };
        }
    };

    const fetchAllSchedules = async () => {
        setIsLoading(true);
        try {
            const schedulesData = await Promise.all(
                blocks.map(async (block) => {
                    const { offerings, validation } = await fetchBlockSchedule(block.block_id);
                    return {
                        block_id: block.block_id,
                        program_id: block.program_id,
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
    }, []);

    useEffect(() => {
        if (blocks.length > 0) {
            fetchAllSchedules();
        }
    }, [blocks]);

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
                <Button variant="primary" onClick={() => setShowGenerateModal(true)}>
                    Generate New Schedule
                </Button>
            </div>

            <ScheduleTable 
                schedules={schedules}
                onView={handleViewSchedule}
                onEdit={handleEditSchedule}
                onValidate={handleValidateSchedule}
                onDelete={handleDeleteSchedule}
                onGenerate={handleGenerateSchedule}
                isLoading={isLoading}
            />

            <ScheduleViewModal
                show={showViewModal}
                blockId={selectedBlock}
                onHide={() => setShowViewModal(false)}
            />

            <ScheduleEditModal
                show={showEditModal}
                blockId={selectedBlock}
                offerings={offerings}
                onHide={() => setShowEditModal(false)}
                onSave={fetchAllSchedules}
            />

            <ScheduleGenerateModal
                show={showGenerateModal}
                blocks={blocks}
                offerings={offerings}
                onHide={() => setShowGenerateModal(false)}
                onGenerate={fetchAllSchedules}
            />
        </Container>
    );
};

export default SchedulePage;
