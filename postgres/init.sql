-- Initialize reports database
CREATE TABLE IF NOT EXISTS report_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_type VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    params JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    file_path VARCHAR(500),
    error_message TEXT
);

-- Index for faster queries
CREATE INDEX idx_report_runs_status ON report_runs(status);
CREATE INDEX idx_report_runs_created_at ON report_runs(created_at DESC);
