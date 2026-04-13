import React, { useState, useEffect, useRef } from 'react';
import { Row, Col, Card, Button, Modal, Form, Alert, Badge } from 'react-bootstrap';
import { FaPlay, FaInfoCircle } from 'react-icons/fa';
import { getReports, runReport, subscribeToRunStatus } from './api';

function Dashboard() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [reportParams, setReportParams] = useState({});
  const [outputFormat, setOutputFormat] = useState('xlsx');
  const [running, setRunning] = useState(false);
  const [success, setSuccess] = useState(null);
  const [liveStatus, setLiveStatus] = useState(null);
  const unsubscribeRef = useRef(null);

  useEffect(() => {
    loadReports();
    
    return () => {
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
      }
    };
  }, []);

  const loadReports = async () => {
    try {
      const data = await getReports();
      setReports(data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load reports');
      setLoading(false);
    }
  };

  const handleRunReport = (report) => {
    setSelectedReport(report);
    setReportParams({});
    setOutputFormat(report.available_formats?.[0] || 'xlsx');
    setSuccess(null);
    setShowModal(true);
  };

  const handleSubmit = async () => {
    try {
      setRunning(true);
      setLiveStatus(null);
      const result = await runReport(selectedReport.id, reportParams, outputFormat);
      setSuccess(`Report "${selectedReport.name}" started!`);
      
      // Subscribe to real-time status updates via SSE
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
      }
      unsubscribeRef.current = subscribeToRunStatus(result.id, (data) => {
        setLiveStatus(data.status);
        if (data.status === 'completed') {
          setSuccess(`Report "${selectedReport.name}" completed successfully!`);
          setRunning(false);
          setTimeout(() => {
            setShowModal(false);
            setSuccess(null);
            setLiveStatus(null);
          }, 2000);
        } else if (data.status === 'failed') {
          setError('Report generation failed: ' + (data.error_message || 'Unknown error'));
          setRunning(false);
        }
      });
    } catch (err) {
      setError('Failed to start report generation');
      setRunning(false);
    }
  };

  const renderParamsForm = (schema) => {
    if (!schema || !schema.properties) {
      return <p className="text-muted">No parameters required</p>;
    }

    return Object.entries(schema.properties).map(([key, prop]) => {
      if (prop.enum) {
        return (
          <Form.Group className="mb-3" key={key}>
            <Form.Label>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</Form.Label>
            <Form.Select
              value={reportParams[key] || prop.default || ''}
              onChange={(e) => setReportParams({ ...reportParams, [key]: e.target.value })}
            >
              {prop.enum.map((option) => (
                <option key={option} value={option}>{option}</option>
              ))}
            </Form.Select>
            <Form.Text className="text-muted">{prop.description}</Form.Text>
          </Form.Group>
        );
      }

      if (prop.type === 'integer') {
        return (
          <Form.Group className="mb-3" key={key}>
            <Form.Label>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</Form.Label>
            <Form.Control
              type="number"
              min={prop.minimum}
              max={prop.maximum}
              value={reportParams[key] || prop.default || ''}
              onChange={(e) => setReportParams({ ...reportParams, [key]: parseInt(e.target.value) })}
            />
            <Form.Text className="text-muted">{prop.description}</Form.Text>
          </Form.Group>
        );
      }

      return (
        <Form.Group className="mb-3" key={key}>
          <Form.Label>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</Form.Label>
          <Form.Control
            type="text"
            value={reportParams[key] || prop.default || ''}
            onChange={(e) => setReportParams({ ...reportParams, [key]: e.target.value })}
          />
          <Form.Text className="text-muted">{prop.description}</Form.Text>
        </Form.Group>
      );
    });
  };

  if (loading) {
    return <div className="text-center py-5"><div className="loading-spinner"></div><p className="mt-2">Loading reports...</p></div>;
  }

  return (
    <div>
      <h2 className="mb-4">Available Reports</h2>
      
      {error && <Alert variant="danger" onClose={() => setError(null)} dismissible>{error}</Alert>}
      
      <Row xs={1} md={2} lg={3} className="g-4">
        {reports.map((report) => (
          <Col key={report.id}>
            <Card className="report-card h-100">
              <Card.Body>
                <Card.Title>{report.name}</Card.Title>
                <Card.Text>{report.description}</Card.Text>
                <div className="d-flex justify-content-between align-items-center mt-3">
                  <Button
                    variant="primary"
                    onClick={() => handleRunReport(report)}
                  >
                    <FaPlay className="me-2" />
                    Generate Report
                  </Button>
                  {report.params_schema && (
                    <Badge bg="info">Configurable</Badge>
                  )}
                </div>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Generate {selectedReport?.name}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {success && <Alert variant="success">{success}</Alert>}
          {error && <Alert variant="danger">{error}</Alert>}
          {liveStatus && liveStatus !== 'completed' && liveStatus !== 'failed' && (
            <Alert variant="info">
              <span className="loading-spinner me-2"></span>
              Status: <strong>{liveStatus.toUpperCase()}</strong>
            </Alert>
          )}
          {selectedReport && selectedReport.available_formats?.length > 1 && (
            <Form.Group className="mb-3">
              <Form.Label>Output Format</Form.Label>
              <Form.Select value={outputFormat} onChange={(e) => setOutputFormat(e.target.value)}>
                {selectedReport.available_formats.map((format) => (
                  <option key={format} value={format}>{format.toUpperCase()}</option>
                ))}
              </Form.Select>
            </Form.Group>
          )}
          {selectedReport && renderParamsForm(selectedReport.params_schema)}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)} disabled={running}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSubmit} disabled={running || success}>
            {running ? (
              <>
                <span className="loading-spinner me-2"></span>
                Starting...
              </>
            ) : (
              <>
                <FaPlay className="me-2" />
                Start Generation
              </>
            )}
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
}

export default Dashboard;
