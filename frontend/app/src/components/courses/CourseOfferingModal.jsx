// CourseOfferingsModal.jsx
import React, { useState, useEffect } from 'react';
import { Modal, Table, Form, Row, Col } from 'react-bootstrap';

const CourseOfferingsModal = ({ show, onHide, courseId }) => {
    const [offerings, setOfferings] = useState([]);
    const [filteredOfferings, setFilteredOfferings] = useState([]);
    const [filters, setFilters] = useState({
        sectionType: '',
        sectionCode: ''
    });
    
    useEffect(() => {
        if (courseId && show) {
            fetchOfferings();
        }
    }, [courseId, show]);
    
    useEffect(() => {
        filterOfferings();
    }, [offerings, filters]);
    
    const fetchOfferings = async () => {
        try {
            const response = await fetch(`http://127.0.0.1:5000/api/offerings/`);
            const data = await response.json();
            const courseOfferings = data.filter(offering => offering.course_id === courseId);
            setOfferings(courseOfferings);
            setFilteredOfferings(courseOfferings);
        } catch (error) {
            console.error('Error fetching offerings:', error);
        }
    };

    const filterOfferings = () => {
        let filtered = [...offerings];
        
        if (filters.sectionType) {
            filtered = filtered.filter(offering => 
                offering.section_type === filters.sectionType
            );
        }
        
        if (filters.sectionCode) {
            filtered = filtered.filter(offering => 
                offering.section_code.toLowerCase().includes(filters.sectionCode.toLowerCase())
            );
        }
        
        setFilteredOfferings(filtered);
    };

    const handleFilterChange = (e) => {
        const { name, value } = e.target;
        setFilters(prev => ({
            ...prev,
            [name]: value
        }));
    };

    return (
        <Modal show={show} onHide={onHide} size="lg">
            <Modal.Header closeButton>
                <Modal.Title>Course Offerings - {courseId}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Row className="mb-3">
                    <Col md={6}>
                        <Form.Group>
                            <Form.Label>Section Type</Form.Label>
                            <Form.Select
                                name="sectionType"
                                value={filters.sectionType}
                                onChange={handleFilterChange}
                            >
                                <option value="">All Types</option>
                                <option value="LECTURE">Lecture</option>
                                <option value="LAB">Lab</option>
                                <option value="TUTORIAL">Tutorial</option>
                            </Form.Select>
                        </Form.Group>
                    </Col>
                    <Col md={6}>
                        <Form.Group>
                            <Form.Label>Section Code</Form.Label>
                            <Form.Control
                                type="text"
                                name="sectionCode"
                                value={filters.sectionCode}
                                onChange={handleFilterChange}
                                placeholder="Filter by section code..."
                            />
                        </Form.Group>
                    </Col>
                </Row>

                <Table striped bordered hover>
                    <thead>
                        <tr>
                            <th>Section</th>
                            <th>Type</th>
                            <th>Day</th>
                            <th>Time</th>
                            <th>Capacity</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredOfferings.map((offering) => (
                            <tr key={offering.offering_id}>
                                <td>{offering.section_code}</td>
                                <td>{offering.section_type}</td>
                                <td>{offering.day_of_week}</td>
                                <td>{`${offering.start_time} - ${offering.end_time}`}</td>
                                <td>{`${offering.current_enrollment}/${offering.capacity}`}</td>
                                <td>{offering.status}</td>
                            </tr>
                        ))}
                    </tbody>
                </Table>
            </Modal.Body>
        </Modal>
    );
};

export default CourseOfferingsModal;
