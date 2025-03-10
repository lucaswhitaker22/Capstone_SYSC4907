import React from 'react';
import { Navbar, Nav, Container, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { QuestionCircle } from 'react-bootstrap-icons';

const Navigation = () => {
  return (
    <Navbar bg="light" expand="lg">
      <Container>
        <Navbar.Brand as={Link} to="/">
          Course Management System
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
          <Nav.Link as={Link} to="/courses">Courses</Nav.Link>
            <Nav.Link as={Link} to="/offerings">Course Offerings</Nav.Link>
            <Nav.Link as={Link} to="/programs">Programs</Nav.Link>
            <Nav.Link as={Link} to="/conflicts">Conflict Checker</Nav.Link>
            <Nav.Link as={Link} to="/schedule">Schedules</Nav.Link>
          </Nav>
          <Nav>
            <OverlayTrigger
              placement="bottom"
              overlay={<Tooltip>Help & Documentation</Tooltip>}
            >
              <Nav.Link as={Link} to="/help">
                <QuestionCircle size={20} />
              </Nav.Link>
            </OverlayTrigger>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Navigation;
