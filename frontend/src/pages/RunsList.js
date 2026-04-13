import React, { useState, useEffect } from 'react';
import { Table, Button, Badge, Alert, Pagination, Container, Row, Col } from 'react-bootstrap';
import { FaDownload, FaSync } from 'react-icons/fa';
import { formatDistanceToNow } from 'date-fns';
import { getRuns, downloadReport } from './api';

function RunsList() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const limit = 20;

  useEffect(() => {
    loadRuns();
  }, [page]);

  const loadRuns = async () => {
    try {
      setLoading(true);
      const data = await getRuns(limit, (page - 1) * limit);
      setRuns(data.runs);
      setTotal(data.total);
      setLoading(false);
    } catch (err) {
      setError('Failed to load report runs');
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      pending: 'secondary',
      running: 'warning',
      completed: 'success',
      failed: 'danger',
    };
    return <Badge bg={variants[status] || 'secondary'} className="status-badge">{status.toUpperCase()}</Badge>;
  };

  const formatTime = (dateString) => {
    if (!dateString) return '-';
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch {
      return dateString;
    }
  };

  const totalPages = Math.ceil(total / limit);

  if (loading && runs.length === 0) {
    return <div className="text-center py-5"><div className="loading-spinner"></div><p className="mt-2">Loading report runs...</p></div>;
  }

  return (
    <Container fluid>
      <Row className="mb-3">
        <Col>
          <h2>Report Runs</h2>
        </Col>
        <Col xs="auto">
          <Button variant="outline-primary" onClick={loadRuns} disabled={loading}>
            <FaSync className={loading ? 'spin' : ''} />
            {loading ? ' Refreshing...' : ' Refresh'}
          </Button>
        </Col>
      </Row>

      {error && <Alert variant="danger" onClose={() => setError(null)} dismissible>{error}</Alert>}

      <div className="runs-table">
        <Table striped bordered hover responsive>
          <thead>
            <tr>
              <th>Run ID</th>
              <th>Report Type</th>
              <th>Status</th>
              <th>Created</th>
              <th>Completed</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {runs.length === 0 ? (
              <tr>
                <td colSpan="6" className="text-center text-muted py-4">
                  No report runs yet. Generate your first report from the Dashboard.
                </td>
              </tr>
            ) : (
              runs.map((run) => (
                <tr key={run.id}>
                  <td><small>{run.id.substring(0, 8)}...</small></td>
                  <td>{run.report_type}</td>
                  <td>{getStatusBadge(run.status)}</td>
                  <td>{formatTime(run.created_at)}</td>
                  <td>{formatTime(run.completed_at)}</td>
                  <td>
                    {run.status === 'completed' ? (
                      <Button
                        variant="success"
                        size="sm"
                        onClick={() => downloadReport(run.id)}
                      >
                        <FaDownload className="me-1" />
                        Download
                      </Button>
                    ) : run.status === 'failed' ? (
                      <small className="text-danger">{run.error_message || 'Failed'}</small>
                    ) : (
                      <small className="text-muted">Processing...</small>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </Table>

        {totalPages > 1 && (
          <Pagination className="justify-content-center mt-3">
            <Pagination.Prev disabled={page === 1} onClick={() => setPage(page - 1)} />
            <Pagination.Item active>{page}</Pagination.Item>
            <Pagination.Next disabled={page >= totalPages} onClick={() => setPage(page + 1)} />
          </Pagination>
        )}
      </div>
    </Container>
  );
}

export default RunsList;
