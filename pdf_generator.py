"""
PDF Generator Module using ReportLab
Creates professional PDF documents from application text
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import io
from datetime import datetime

def generate_pdf(application_text, college_name):
    """
    Generate a PDF file from application text
    Returns a BytesIO buffer containing the PDF
    """
    # Create a buffer to hold PDF data
    buffer = io.BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Container for story elements
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=30,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        leading=14,
        fontName='Helvetica'
    )
    
    # Add college header
    header_text = f"<b>{college_name.upper()}</b><br/>"
    header_text += "APPLICATION LETTER<br/>"
    header_text += f"Date: {datetime.now().strftime('%d/%m/%Y')}"
    
    header = Paragraph(header_text, title_style)
    story.append(header)
    story.append(Spacer(1, 0.2 * inch))
    
    # Add separator line
    #story.append(Paragraph("<hr/>", body_style))
    story.append(Spacer(1, 0.3 * inch))
    
    # Process application text and add to PDF
    # Split text into lines and preserve formatting
    lines = application_text.split('\n')
    
    for line in lines:
        if line.strip():
            # Check if it's a subject line or important header
            if line.strip().startswith('Subject:') or line.strip().startswith('To,') or \
               line.strip().startswith('Respected') or line.strip().startswith('Thanking'):
                # Use bold for important sections
                bold_style = ParagraphStyle(
                    'BoldStyle',
                    parent=body_style,
                    fontName='Helvetica-Bold'
                )
                story.append(Paragraph(line.replace('\n', '<br/>'), bold_style))
            else:
                story.append(Paragraph(line.replace('\n', '<br/>'), body_style))
            story.append(Spacer(1, 0.1 * inch))
    
    # Add footer
    story.append(Spacer(1, 0.05 * inch))
   
    footer_text = "<i>This is a computer-generated application. No signature required.</i>"
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        textColor='gray'
    )
    story.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(story)
    
    # Get buffer value and close
    buffer.seek(0)
    
    return buffer