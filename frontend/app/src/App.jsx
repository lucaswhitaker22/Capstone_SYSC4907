import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import Navigation from './components/shared/Navigation';
import OfferingsPage from './components/offerings/OfferingPage';
import BlocksPage from './components/blocks/BlocksPage';
import ProgramsPage from './components/programs/ProgramsPage';
import ConflictsPage from './components/conflicts/ConflictsPage';
import SchedulePage from './components/schedule/SchedulePage';
import CoursesPage from './components/courses/CoursesPage';
const HomePage = () => {
  const navigate = useNavigate();

  const pages = [
    {
      title: "Courses",
      description: "Manage course information and basic details",
      path: "/courses",
      variant: "primary"
    },
    {
      title: "Course Offerings",
      description: "Handle course sections, schedules, and enrollment capacities",
      path: "/offerings",
      variant: "success"
    },
    {
      title: "Programs",
      description: "Manage programs, requirements, and student allocations",
      path: "/programs",
      variant: "info"
    },
    {
      title: "Blocks",
      description: "Manage blocks and manage their schedules",
      path: "/blocks",
      variant: "warning"
    },
    {
      title: "Conflicts",
      description: "Detect conflicts between courses/schedules",
      path: "/conflicts",
      variant: "danger"
    },
    {
      title: "Schedule",
      description: "View and manage block schedules",
      path: "/schedule",
      variant: "secondary"
    }
  ];

  return (
    <Container className="py-5">
      <h1 className="text-center mb-4">Course Management System</h1>
      <Row xs={1} md={2} lg={3} className="g-4">
        {pages.map((page, idx) => (
          <Col key={idx}>
            <Card className="h-100 shadow-sm">
              <Card.Body className="d-flex flex-column">
                <Card.Title>{page.title}</Card.Title>
                <Card.Text className="flex-grow-1">{page.description}</Card.Text>
                <Button
                  variant={page.variant}
                  onClick={() => navigate(page.path)}
                  className="w-100"
                >
                  Go to {page.title}
                </Button>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
};

const App = () => {
  return (
    <div className="d-flex flex-column min-vh-100">
      <BrowserRouter>
        <Navigation />
        <Container fluid className="flex-grow-1">
          <Routes>
            <Route path="/offerings" element={<OfferingsPage />} />
            <Route path="/blocks" element={<BlocksPage />} />
            <Route path="/courses" element={<CoursesPage />} />
            <Route path="/programs" element={<ProgramsPage />} />
            <Route path="/conflicts" element={<ConflictsPage />} />
            <Route path="/schedule" element={<SchedulePage />} />
            <Route path="/" element={<HomePage />} />
          </Routes>
        </Container>

        <footer
          className="mt-auto bg-secondary bg-opacity-10 text-dark"
          style={{
            height: '40px',
            display: 'flex',
            alignItems: 'center',
            padding: '0'
          }}
        >
          <Container className="h-100">
            <Row className="align-items-center h-100">
              <Col md={4} className="d-flex justify-content-center justify-content-md-start h-100 align-items-center">
                <img
                  src="https://ddfoqzqsu0zvp.cloudfront.net/media/documents/carleton_black_1.png"
                  alt="Carleton University Logo"
                  style={{
                    maxWidth: '80px',
                    height: 'auto'
                  }}
                />
              </Col>
              <Col md={4} className="text-center h-100 d-flex align-items-center justify-content-center">
                <div>
                  <span className="small">SYSC4907A Engineering Capstone Project</span>
                  
                </div>
              </Col>
              <Col md={4} className="text-center text-md-end h-100 d-flex align-items-center justify-content-end">
                <div>
                <b className="small me-2"> &copy; 2025 Lucas Whitaker</b> 
                <small className="text-muted small">Version 1.0.0</small>
                </div>
              </Col>
            </Row>
          </Container>
        </footer>





      </BrowserRouter>
    </div>
  );
};


export default App;
