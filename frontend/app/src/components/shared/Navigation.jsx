import React from 'react';
import { Navbar, Nav, Container } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const Navigation = () => {
  return (
    <Navbar bg="dark" variant="dark" expand="lg" className="mb-4">
      <Container>
        <Navbar.Brand as={Link} to="/">Course Management System</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link as={Link} to="/offerings">Course Offerings</Nav.Link>
            <Nav.Link as={Link} to="/courses">Courses</Nav.Link>

            <Nav.Link as={Link} to="/blocks">Blocks</Nav.Link>
            <Nav.Link as={Link} to="/programs">Programs</Nav.Link>
            <Nav.Link as={Link} to="/conflicts">Conflict Checker</Nav.Link>
            <Nav.Link as={Link} to="/schedule">Schedules</Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Navigation;
