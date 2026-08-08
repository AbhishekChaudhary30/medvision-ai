"""Report generation service."""

import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.analysis import Analysis


def generate_analysis_report(analysis: Analysis) -> bytes:
    """Generate a PDF report for a given analysis."""
    buffer = io.BytesIO()
    
    # Setup document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    title_style.alignment = 1  # Center
    
    h2_style = styles["Heading2"]
    
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        textColor=colors.red,
        fontSize=9,
        leading=12
    )
    
    story = []
    
    # Header
    story.append(Paragraph("MedVision AI - Analysis Report", title_style))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "This system is a research/educational clinical decision-support prototype and is not a substitute for professional medical diagnosis.",
        disclaimer_style
    ))
    story.append(Spacer(1, 0.5 * inch))
    
    # Analysis Metadata
    story.append(Paragraph("Analysis Information", h2_style))
    metadata_data = [
        ["Analysis ID", str(analysis.id)],
        ["Date", analysis.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")],
        ["Model Version", analysis.model_version],
        ["Model Architecture", analysis.model_architecture]
    ]
    
    metadata_table = Table(metadata_data, colWidths=[2 * inch, 4 * inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(metadata_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Prediction Results
    story.append(Paragraph("Prediction Results", h2_style))
    prediction_data = [
        ["Model Prediction", analysis.predicted_class],
        ["Confidence", f"{analysis.confidence * 100:.2f}%"],
        ["Probability NORMAL", f"{analysis.probability_normal * 100:.2f}%"],
        ["Probability PNEUMONIA", f"{analysis.probability_pneumonia * 100:.2f}%"],
        ["Uncertainty Status", analysis.uncertainty_status],
    ]
    
    prediction_table = Table(prediction_data, colWidths=[2 * inch, 4 * inch])
    prediction_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(prediction_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Review Information (if available)
    if analysis.review_status != "NOT_REVIEWED":
        story.append(Paragraph("Review Information", h2_style))
        
        review_data = [
            ["Review Status", analysis.review_status],
            ["Reviewed At", analysis.reviewed_at.strftime("%Y-%m-%d %H:%M:%S UTC") if analysis.reviewed_at else "N/A"],
            ["Reviewer Notes", analysis.reviewer_notes or "None"]
        ]
        
        review_table = Table(review_data, colWidths=[2 * inch, 4 * inch])
        review_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(review_table)
        story.append(Spacer(1, 0.3 * inch))
    
    # Build document
    doc.build(story)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
