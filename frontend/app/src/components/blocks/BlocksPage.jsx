import React, { useState, useEffect } from 'react';
import { Container, Button } from 'react-bootstrap';
import BlocksTable from './BlocksTable';
import BlocksModal from './BlocksModal';
import BlockScheduleModal from './BlockScheduleModal';
const API_URL = 'http://127.0.0.1:5000/api';

const BlocksPage = () => {
    const [blocks, setBlocks] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [showScheduleModal, setShowScheduleModal] = useState(false);
    const [selectedBlock, setSelectedBlock] = useState(null);
    const [selectedBlockId, setSelectedBlockId] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
  

  const fetchBlocks = async () => {
    try {
      const response = await fetch(`${API_URL}/blocks`);
      const data = await response.json();
      setBlocks(data);
    } catch (error) {
      console.error('Error fetching blocks:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBlocks();
  }, []);

  const handleAddNew = () => {
    setSelectedBlock(null);
    setShowModal(true);
  };

  const handleEdit = (block) => {
    setSelectedBlock(block);
    setShowModal(true);
  };

  const handleDelete = async (blockId) => {
    if (window.confirm('Are you sure you want to delete this block?')) {
      try {
        const response = await fetch(`${API_URL}/blocks/${blockId}`, {
          method: 'DELETE'
        });
        if (response.ok) {
          await fetchBlocks();
        } else {
          const error = await response.json();
          alert(error.error || 'Error deleting block');
        }
      } catch (error) {
        console.error('Error deleting block:', error);
      }
    }
  };

  const handleCalculateRating = async (blockId) => {
    try {
        const response = await fetch(`${API_URL}/schedules/block/${blockId}/rate`, {
            method: 'GET'
        });
        
        if (response.ok) {
            const rating = await response.json();
            // Update the blocks with the new rating
            setBlocks(blocks.map(block => 
                block.block_id === blockId 
                    ? { ...block, schedule_rating: rating } 
                    : block
            ));
        } else {
            const error = await response.json();
            alert(error.error || 'Error calculating rating');
        }
    } catch (error) {
        console.error('Error calculating rating:', error);
        alert('Error calculating schedule rating');
    }
};


  const handleViewSchedule = (blockId) => {
    setSelectedBlockId(blockId);
    setShowScheduleModal(true);
  };

  const handleSave = async (formData) => {
    try {
      const method = selectedBlock ? 'PUT' : 'POST';
      const url = selectedBlock 
        ? `${API_URL}/blocks/${selectedBlock.block_id}`
        : `${API_URL}/blocks`;

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setShowModal(false);
        await fetchBlocks();
      } else {
        const error = await response.json();
        alert(error.error || 'Error saving block');
      }
    } catch (error) {
      console.error('Error saving block:', error);
    }
  };

  const handleStatusUpdate = async (blockId, status) => {
    try {
      const response = await fetch(`${API_URL}/blocks/${blockId}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status }),
      });

      if (response.ok) {
        await fetchBlocks();
      } else {
        const error = await response.json();
        alert(error.error || 'Error updating status');
      }
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  return (
    <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Block Management</h1>
        <Button variant="primary" onClick={handleAddNew}>
          Create New Block
        </Button>
      </div>

      <BlocksTable 
        blocks={blocks}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onViewSchedule={handleViewSchedule}
        onCalculateRating={handleCalculateRating}
        onStatusUpdate={handleStatusUpdate}
        isLoading={isLoading}
      />

      <BlocksModal
        show={showModal}
        block={selectedBlock}
        onHide={() => setShowModal(false)}
        onSave={handleSave}
      />
            <BlockScheduleModal
        show={showScheduleModal}
        blockId={selectedBlockId}
        onHide={() => setShowScheduleModal(false)}
      />
    </Container>
  );
};

export default BlocksPage;
