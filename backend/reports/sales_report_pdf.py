from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import random
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from reports.base import BaseReportGenerator


class SalesReportPdfGenerator(BaseReportGenerator):
    """Sales report - generates PDF with sales data for a given period."""
    
    @property
    def id(self) -> str:
        return "sales_report"
    
    @property
    def name(self) -> str:
        return "Sales Report (PDF)"
    
    @property
    def description(self) -> str:
        return "Comprehensive sales report with revenue breakdown by product and region (PDF format)"
    
    @property
    def params_schema(self) -> Optional[Dict[str, Any]]:
        return {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of days to include in the report",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 365
                },
                "region": {
                    "type": "string",
                    "description": "Filter by region (optional)",
                    "enum": ["North", "South", "East", "West", "All"]
                }
            }
        }
    
    async def generate(self, params: Dict[str, Any], output_path: str) -> str:
        # Ensure .pdf extension
        if not output_path.endswith('.pdf'):
            output_path = output_path.rsplit('.', 1)[0] + '.pdf'
        
        days = params.get("days", 30)
        region_filter = params.get("region", "All")
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=18,
            textColor=colors.HexColor('#2F5496'),
            spaceAfter=6,
        )
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            spaceAfter=12,
        )
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2F5496'),
            spaceBefore=18,
            spaceAfter=8,
        )
        
        story = []
        
        # Title
        story.append(Paragraph(f"Sales Report - Last {days} days", title_style))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Region: {region_filter}",
            subtitle_style
        ))
        story.append(Spacer(1, 12))
        
        # Generate mock data
        products = ["Product A", "Product B", "Product C", "Product D", "Product E"]
        regions = ["North", "South", "East", "West"]
        if region_filter != "All":
            regions = [region_filter]
        
        # Summary metrics table
        story.append(Paragraph("Key Metrics", section_style))
        
        metrics_data = [
            ["Metric", "Value"],
            ["Total Revenue", f"${random.uniform(300000, 1500000):,.2f}"],
            ["Total Orders", f"{random.randint(100, 500) * len(regions):,}"],
            ["Average Order Value", f"${random.uniform(100, 500):,.2f}"],
            ["Conversion Rate", f"{random.uniform(2.0, 8.0):.2f}%"],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2F5496')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(metrics_table)
        
        # Revenue by Product
        story.append(Paragraph("Revenue by Product", section_style))
        
        product_data = [["Product", "Units Sold", "Revenue", "Growth %"]]
        for product in products:
            units = random.randint(50, 500)
            revenue = units * random.uniform(20, 200)
            growth = random.uniform(-10, 30)
            product_data.append([
                product,
                f"{units:,}",
                f"${revenue:,.2f}",
                f"{growth:.1f}%"
            ])
        
        product_table = Table(product_data, colWidths=[1.8*inch, 1.2*inch, 1.5*inch, 1*inch])
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2F5496')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(product_table)
        
        # Revenue by Region
        story.append(Paragraph("Revenue by Region", section_style))
        
        total_revenue = sum(random.uniform(10000, 50000) for _ in range(len(regions)))
        region_data = [["Region", "Orders", "Revenue", "% of Total"]]
        for region in regions:
            orders = random.randint(50, 300)
            revenue = random.uniform(5000, 25000)
            pct = (revenue / total_revenue) * 100
            region_data.append([
                region,
                f"{orders:,}",
                f"${revenue:,.2f}",
                f"{pct:.1f}%"
            ])
        
        region_table = Table(region_data, colWidths=[1.8*inch, 1.2*inch, 1.5*inch, 1*inch])
        region_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2F5496')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(region_table)
        
        # Daily Trends
        story.append(PageBreak())
        story.append(Paragraph("Daily Trends", section_style))
        
        trends_data = [["Date", "Revenue", "Orders", "Avg Order Value"]]
        base_date = datetime.now() - timedelta(days=days)
        for i in range(min(days, 30)):  # Limit to 30 rows for readability
            date = base_date + timedelta(days=i)
            revenue = random.uniform(1000, 5000)
            orders = random.randint(10, 100)
            avg_order = revenue / orders
            trends_data.append([
                date.strftime('%Y-%m-%d'),
                f"${revenue:,.2f}",
                f"{orders}",
                f"${avg_order:,.2f}"
            ])
        
        trends_table = Table(trends_data, colWidths=[1.3*inch, 1.3*inch, 1*inch, 1.4*inch])
        trends_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2F5496')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(trends_table)
        
        doc.build(story)
        return output_path
