import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import Navigation from './components/shared/Navigation';
import OfferingsPage from './components/offerings/OfferingPage';
import BlocksPage from './components/blocks/BlocksPage';
import ProgramsPage from './components/programs/ProgramsPage';
import ConflictsPage from './components/conflicts/ConflictsPage';
import SchedulePage from './components/schedule/SchedulePage';
import CoursesPage from './components/courses/CoursesPage';
const App = () => {
  return (
    <BrowserRouter>
      <Navigation />
      <Container fluid>
        <Routes>
          <Route path="/offerings" element={<OfferingsPage />} />
          <Route path="/blocks" element={<BlocksPage/>} />
          <Route path="/courses" element={<CoursesPage/>} />

          <Route path="/programs" element={<ProgramsPage/>} />
          <Route path="/conflicts" element={<ConflictsPage/>} />
          <Route path="/schedule" element={<SchedulePage/>} />
          <Route path="/" element={<div>Welcome to Course Management System</div>} />
        </Routes>
      </Container>
    </BrowserRouter>
  );
};

export default App;
