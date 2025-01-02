// ProgramUploadModal.jsx
import React, { useState } from 'react';
import { Modal, Button, Table, Alert } from 'react-bootstrap';
import Papa from 'papaparse';

const ProgramUploadModal = ({ show, onHide, onSave }) => {
    const [parsedData, setParsedData] = useState([]);
    const [error, setError] = useState(null);

    const handleFileUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            Papa.parse(file, {
                header: true,
                skipEmptyLines: true,
                complete: (results) => {
                    if (results.errors.length > 0) {
                        setError('Error parsing CSV file');
                        return;
                    }
                    const validData = results.data.map(item => ({
                        ...item,
                        total_enrollment: parseInt(item.total_enrollment),
                        blocks_20_count: parseInt(item.blocks_20_count),
                        blocks_10_count: parseInt(item.blocks_10_count)
                    }));
                    setParsedData(validData);
                    setError(null);
                }
            });
        }
    };

    const handleSave = async () => {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/programs/bulk', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ programs: parsedData })
            });
            if (response.ok) {
                onSave();
                onHide();
            } else {
                const error = await response.json();
                setError(error.message || 'Error uploading programs');
            }
        } catch (error) {
            setError('Error uploading programs');
        }
    };

    return (
        <Modal show={show} onHide={onHide} size="lg">
            <Modal.Header closeButton>
                <Modal.Title>Upload Programs CSV</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileUpload}
                    className="mb-3"
                />
                {error && (
                    <Alert variant="danger">{error}</Alert>
                )}
                {parsedData.length > 0 && (
                    <Table striped bordered hover>
                        <thead>
                            <tr>
                                <th>Program ID</th>
                                <th>Program Name</th>
                                <th>Total Enrollment</th>
                                <th>20-Student Blocks</th>
                                <th>10-Student Blocks</th>
                            </tr>
                        </thead>
                        <tbody>
                            {parsedData.map((program, index) => (
                                <tr key={index}>
                                    <td>{program.program_id}</td>
                                    <td>{program.program_name}</td>
                                    <td>{program.total_enrollment}</td>
                                    <td>{program.blocks_20_count}</td>
                                    <td>{program.blocks_10_count}</td>
                                </tr>
                            ))}
                        </tbody>
                    </Table>
                )}
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={onHide}>Cancel</Button>
                <Button 
                    variant="primary" 
                    onClick={handleSave}
                    disabled={parsedData.length === 0}
                >
                    Save Programs
                </Button>
            </Modal.Footer>
        </Modal>
    );
};

export default ProgramUploadModal;
