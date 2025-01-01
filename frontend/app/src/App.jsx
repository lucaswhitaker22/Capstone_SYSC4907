import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import Navigation from './components/Navigation';
import OfferingsPage from './components/offerings/OfferingPage';
import BlocksPage from './components/blocks/BlocksPage';
const App = () => {
  return (
    <BrowserRouter>
      <Navigation />
      <Container fluid>
        <Routes>
          <Route path="/offerings" element={<OfferingsPage />} />
          <Route path="/blocks" element={<BlocksPage/>} />
          <Route path="/programs" element={<div>Programs Page</div>} />
          <Route path="/" element={<div>Welcome to Course Management System</div>} />
        </Routes>
      </Container>
    </BrowserRouter>
  );
};

export default App;
