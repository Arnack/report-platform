"""Integration tests for API endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint returns API info."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data


@pytest.mark.asyncio
async def test_list_available_reports(client: AsyncClient):
    """Test listing available report types."""
    response = await client.get("/api/reports")
    assert response.status_code == 200
    
    reports = response.json()
    assert len(reports) >= 2  # At least our 2 reports
    
    # Verify report structure
    report_ids = [r["id"] for r in reports]
    assert "sales_report" in report_ids
    assert "api_usage_report" in report_ids
    
    # Each report should have required fields
    for report in reports:
        assert "id" in report
        assert "name" in report
        assert "description" in report


@pytest.mark.asyncio
async def test_run_report(client: AsyncClient):
    """Test triggering report generation."""
    response = await client.post(
        "/api/reports/sales_report/run",
        json={"params": {"days": 7}}
    )
    assert response.status_code == 202
    
    data = response.json()
    assert "id" in data
    assert data["report_type"] == "sales_report"
    assert data["status"] in ["pending", "running"]


@pytest.mark.asyncio
async def test_run_report_invalid_type(client: AsyncClient):
    """Test running non-existent report type."""
    response = await client.post(
        "/api/reports/nonexistent_report/run",
        json={"params": {}}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_runs_empty(client: AsyncClient):
    """Test listing runs when none exist."""
    response = await client.get("/api/runs")
    assert response.status_code == 200
    
    data = response.json()
    assert "runs" in data
    assert "total" in data
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_get_run_not_found(client: AsyncClient):
    """Test getting non-existent run."""
    response = await client.get("/api/runs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_download_not_found(client: AsyncClient):
    """Test downloading non-existent run."""
    response = await client.get("/api/runs/00000000-0000-0000-0000-000000000000/download")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_run_report_with_default_params(client: AsyncClient):
    """Test running report without params (should use defaults)."""
    response = await client.post(
        "/api/reports/api_usage_report/run",
        json={}
    )
    assert response.status_code == 202
    
    data = response.json()
    assert data["report_type"] == "api_usage_report"


@pytest.mark.asyncio
async def test_runs_pagination(client: AsyncClient):
    """Test runs list with pagination."""
    # Create multiple runs
    for i in range(5):
        await client.post(
            "/api/reports/sales_report/run",
            json={"params": {"days": i + 1}}
        )
    
    response = await client.get("/api/runs?limit=2&offset=0")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 5
    assert len(data["runs"]) == 2
