// CourseOfferingsModal.jsx
import React, { useState, useEffect } from 'react';
import { Modal, Table, Form, Row, Col } from 'react-bootstrap';

const CourseOfferingsModal = ({ show, onHide, courseId }) => {
    const [offerings, setOfferings] = useState([]);
    const [filteredOfferings, setFilteredOfferings] = useState([]);
    const [availableYears, setAvailableYears] = useState([]);

    const [filters, setFilters] = useState({
        sectionType: '',
        sectionCode: '',
        term: '',
        academic_year: ''
    });
    
    useEffect(() => {
        if (courseId && show) {
            fetchOfferings();
        }
    }, [courseId, show]);
    
    useEffect(() => {
        filterOfferings();
    }, [offerings, filters]);
    useEffect(() => {
        // Extract unique academic years from offerings
        if (offerings.length > 0) {
            const years = [...new Set(offerings.map(o => o.academic_year))];
            setAvailableYears(years.sort());
        }
    }, [offerings]);
    
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

        if (filters.term) {
            filtered = filtered.filter(offering => 
                offering.term === filters.term
            );
        }

        if (filters.academic_year) {
            filtered = filtered.filter(offering => 
                offering.academic_year === filters.academic_year
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
                <Col md={4}>
                        <Form.Group>
                            <Form.Label>Term</Form.Label>
                            <Form.Select
                                name="term"
                                value={filters.term}
                                onChange={handleFilterChange}
                            >
                                <option value="">All Terms</option>
                                <option value="FALL">Fall</option>
                                <option value="WINTER">Winter</option>
                            </Form.Select>
                        </Form.Group>
                    </Col>
                    <Col md={4}>
                        <Form.Group>
                            <Form.Label>Academic Year</Form.Label>
                            <Form.Select
                                name="academic_year"
                                value={filters.academic_year}
                                onChange={handleFilterChange}
                            >
                                <option value="">All Years</option>
                                {availableYears.map(year => (
                                    <option key={year} value={year}>{year}</option>
                                ))}
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
                            <th>Term</th>
                            <th>Academic Year</th>
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
                                <td>{offering.term}</td>
                                <td>{offering.academic_year}</td>
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
