from typing import Dict, Type
from reports.base import BaseReportGenerator
from reports.sales_report import SalesReportGenerator
from reports.api_usage_report import APIUsageReportGenerator

# Registry of all available report generators
REPORT_REGISTRY: Dict[str, Type[BaseReportGenerator]] = {
    SalesReportGenerator().id: SalesReportGenerator,
    APIUsageReportGenerator().id: APIUsageReportGenerator,
}


def get_report_generator(report_id: str) -> BaseReportGenerator:
    """Get a report generator instance by ID."""
    if report_id not in REPORT_REGISTRY:
        raise ValueError(f"Unknown report type: {report_id}. Available: {list(REPORT_REGISTRY.keys())}")
    return REPORT_REGISTRY[report_id]()


def get_all_reports():
    """Get information about all available reports."""
    return [generator_cls() for generator_cls in REPORT_REGISTRY.values()]
