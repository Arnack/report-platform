from typing import Dict, Type
from reports.base import BaseReportGenerator
from reports.sales_report import SalesReportGenerator
from reports.api_usage_report import APIUsageReportGenerator
from reports.sales_report_pdf import SalesReportPdfGenerator

# Registry of all available report generators
REPORT_REGISTRY: Dict[str, Type[BaseReportGenerator]] = {
    "sales_report_xlsx": SalesReportGenerator,
    "api_usage_report_xlsx": APIUsageReportGenerator,
    "sales_report_pdf": SalesReportPdfGenerator,
}

# Map logical report IDs to format-specific generators
REPORT_FORMAT_MAP: Dict[str, Dict[str, Type[BaseReportGenerator]]] = {
    "sales_report": {
        "xlsx": SalesReportGenerator,
        "pdf": SalesReportPdfGenerator,
    },
    "api_usage_report": {
        "xlsx": APIUsageReportGenerator,
    },
}


def get_report_generator(report_id: str, output_format: str = "xlsx") -> BaseReportGenerator:
    """Get a report generator instance by ID and format."""
    if report_id in REPORT_FORMAT_MAP:
        formats = REPORT_FORMAT_MAP[report_id]
        if output_format not in formats:
            raise ValueError(
                f"Format '{output_format}' not available for '{report_id}'. "
                f"Available: {list(formats.keys())}"
            )
        return formats[output_format]()
    
    # Fallback to legacy lookup
    key = f"{report_id}_{output_format}"
    if key not in REPORT_REGISTRY:
        raise ValueError(f"Unknown report type: {report_id} ({output_format}). Available: {list(REPORT_REGISTRY.keys())}")
    return REPORT_REGISTRY[key]()


def get_available_formats(report_id: str) -> list[str]:
    """Get available output formats for a report type."""
    if report_id in REPORT_FORMAT_MAP:
        return list(REPORT_FORMAT_MAP[report_id].keys())
    return ["xlsx"]  # Default fallback


def get_all_reports():
    """Get information about all available reports (one entry per logical report type)."""
    reports = []
    seen_ids = set()
    
    for report_id, format_map in REPORT_FORMAT_MAP.items():
        # Use the first format's generator for metadata
        first_format = list(format_map.keys())[0]
        generator = format_map[first_format]()
        
        if generator.id not in seen_ids:
            reports.append(generator)
            seen_ids.add(generator.id)
    
    return reports
