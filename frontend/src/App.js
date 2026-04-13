import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Container, Navbar, Nav as RBNav } from 'react-bootstrap';
import Dashboard from './pages/Dashboard';
import RunsList from './pages/RunsList';
import './App.css';

function App() {
  return (
    <Router>
      <Navbar bg="dark" variant="dark" expand="lg" className="mb-4">
        <Container>
          <Navbar.Brand href="/">Report Platform</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <RBNav className="me-auto">
              <RBNav.Link href="/">Dashboard</RBNav.Link>
              <RBNav.Link href="/runs">Report Runs</RBNav.Link>
            </RBNav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
      
      <Container>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/runs" element={<RunsList />} />
        </Routes>
      </Container>
    </Router>
  );
}

export default App;
