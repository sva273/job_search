from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from io import BytesIO
import os
from .models import JobEntry

# Register font with Cyrillic support
# Use system font or built-in font with Unicode support
def _register_cyrillic_font():
    """Register font with Cyrillic support"""
    try:
        # Try to use system fonts with Cyrillic support
        font_paths = [
            # macOS - Arial and other fonts with Unicode support
            '/System/Library/Fonts/Supplemental/Arial.ttf',
            '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
            '/Library/Fonts/Arial.ttf',
            '/Library/Fonts/Arial Bold.ttf',
            '/System/Library/Fonts/Helvetica.ttc',
            # Linux - DejaVu and Liberation support Cyrillic
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
            # Windows - Arial and Arial Unicode MS
            'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/arialbd.ttf',
            'C:/Windows/Fonts/arialuni.ttf',  # Arial Unicode MS - full Unicode support
            'C:/Windows/Fonts/times.ttf',
        ]
        
        regular_font = None
        bold_font = None
        
        # Find regular font
        for font_path in font_paths:
            if os.path.exists(font_path) and 'Bold' not in font_path and 'bd' not in font_path.lower():
                try:
                    pdfmetrics.registerFont(TTFont('CyrillicFont', font_path))
                    regular_font = 'CyrillicFont'
                    break
                except Exception:
                    continue
        
        # Find bold font
        for font_path in font_paths:
            if os.path.exists(font_path) and ('Bold' in font_path or 'bd' in font_path.lower()):
                try:
                    pdfmetrics.registerFont(TTFont('CyrillicFontBold', font_path))
                    bold_font = 'CyrillicFontBold'
                    break
                except Exception:
                    continue
        
        # If bold font not found, use regular font
        if regular_font and not bold_font:
            try:
                # Use the same font for bold
                for font_path in font_paths:
                    if os.path.exists(font_path) and 'Bold' not in font_path and 'bd' not in font_path.lower():
                        pdfmetrics.registerFont(TTFont('CyrillicFontBold', font_path))
                        bold_font = 'CyrillicFontBold'
                        break
            except Exception:
                pass
        
        if regular_font:
            return regular_font
        
        # If system fonts not found, return None
        return None
    except Exception:
        return None

# Register font when module is imported
CYRILLIC_FONT = _register_cyrillic_font()
CYRILLIC_FONT_BOLD = 'CyrillicFontBold' if CYRILLIC_FONT == 'CyrillicFont' else None

# If font not found, use alternative approach with CID fonts
if not CYRILLIC_FONT:
    try:
        # Use CID fonts that support Unicode (including Cyrillic)
        # ReportLab has built-in CID fonts for Cyrillic
        pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))  # Japanese font, but supports Unicode
        pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W6'))  # Bold version
        CYRILLIC_FONT = 'HeiseiKakuGo-W5'
        CYRILLIC_FONT_BOLD = 'HeiseiKakuGo-W6'
    except:
        # If CID fonts don't work, use standard fonts (but they don't support Cyrillic)
        CYRILLIC_FONT = 'Helvetica'
        CYRILLIC_FONT_BOLD = 'Helvetica-Bold'


def generate_job_pdf(job_entry: JobEntry, language_code: str = 'ru') -> BytesIO:
    """
    Generate PDF document with job entry information
    
    Args:
        job_entry: JobEntry model instance
        language_code: Language code (ru, en, de)
        
    Returns:
        BytesIO: Byte stream with PDF content
    """
    from django.utils import translation
    
    # Activate language for translations
    old_language = translation.get_language()
    translation.activate(language_code)
    
    # Use translation.gettext directly to ensure correct language is used
    def _(text):
        return translation.gettext(text)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Styles with Cyrillic support
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=CYRILLIC_FONT_BOLD,
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=CYRILLIC_FONT_BOLD,
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=CYRILLIC_FONT,
        fontSize=11,
        leading=14
    )
    
    # Title
    story.append(Paragraph(translation.gettext("Job Information"), title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Basic information
    data = [
        [f"{translation.gettext('Job Title')}:", job_entry.job_title or translation.gettext('Not specified')],
        [f"{translation.gettext('Employer')}:", job_entry.employer or translation.gettext('Not specified')],
        [f"{translation.gettext('Address')}:", job_entry.address or translation.gettext('Not specified')],
    ]
    
    if job_entry.contact_email:
        data.append([f"{translation.gettext('Contact Email')}:", job_entry.contact_email])
    if job_entry.contact_phone:
        data.append([f"{translation.gettext('Phone')}:", job_entry.contact_phone])
    if job_entry.company_website:
        data.append([f"{translation.gettext('Company Website')}:", job_entry.company_website])
    
    data.append([f"{translation.gettext('Job URL')}:", job_entry.job_url])
    
    table = Table(data, colWidths=[2*inch, 4.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), CYRILLIC_FONT_BOLD),
        ('FONTNAME', (1, 0), (1, -1), CYRILLIC_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.3*inch))
    
    # Description
    if job_entry.description:
        story.append(Paragraph(translation.gettext("Description"), heading_style))
        # Clean HTML tags from description for safe display
        description_text = job_entry.description.replace('<', '&lt;').replace('>', '&gt;')
        story.append(Paragraph(description_text, normal_style))
        story.append(Spacer(1, 0.2*inch))
    
    # Creation date
    story.append(Spacer(1, 0.3*inch))
    date_text = f"{translation.gettext('Created')}: {job_entry.created_at.strftime('%d.%m.%Y %H:%M')}"
    story.append(Paragraph(date_text, ParagraphStyle(
        'DateStyle',
        parent=normal_style,
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )))
    
    # Restore previous language
    translation.activate(old_language)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_statistics_pdf(statistics_data: dict, username: str, language_code: str = 'ru') -> BytesIO:
    """
    Generate PDF document with job statistics
    
    Args:
        statistics_data: Dictionary with statistics data
        username: Username
        language_code: Language code (ru, en, de)
        
    Returns:
        BytesIO: Byte stream with PDF content
    """
    from django.utils import translation
    from datetime import datetime
    
    # Activate language for translations
    old_language = translation.get_language()
    translation.activate(language_code)
    
    # Use translation.gettext directly to ensure correct language is used
    def _(text):
        return translation.gettext(text)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Styles with Cyrillic support
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=CYRILLIC_FONT_BOLD,
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=CYRILLIC_FONT_BOLD,
        fontSize=16,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=16
    )
    
    subheading_style = ParagraphStyle(
        'SubHeading',
        parent=styles['Heading3'],
        fontName=CYRILLIC_FONT_BOLD,
        fontSize=12,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=8,
        spaceBefore=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=CYRILLIC_FONT,
        fontSize=10,
        leading=14
    )
    
    # Title
    story.append(Paragraph(translation.gettext("Statistics"), title_style))
    story.append(Paragraph(f"{translation.gettext('User')}: {username}", ParagraphStyle(
        'UserStyle',
        parent=normal_style,
        fontSize=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#7f8c8d')
    )))
    story.append(Paragraph(f"{translation.gettext('Report Date')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ParagraphStyle(
        'DateStyle',
        parent=normal_style,
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.grey
    )))
    story.append(Spacer(1, 0.3*inch))
    
    # General statistics
    story.append(Paragraph(translation.gettext("General Statistics"), heading_style))
    general_data = [
        [f"{translation.gettext('Total Jobs')}:", str(statistics_data['total_jobs'])],
        [f"{translation.gettext('Resumes Submitted')}:", str(statistics_data['resume_submitted_count'])],
        [f"{translation.gettext('Responses Received')}:", str(statistics_data['response_received_count'])],
        [f"{translation.gettext('Rejections')}:", str(statistics_data['rejection_received_count'])],
    ]
    
    general_table = Table(general_data, colWidths=[3*inch, 3.5*inch])
    general_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), CYRILLIC_FONT_BOLD),
        ('FONTNAME', (1, 0), (1, -1), CYRILLIC_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(general_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Status statistics
    story.append(Paragraph(translation.gettext("Status Distribution"), heading_style))
    status_data = [
        [translation.gettext("Status"), translation.gettext("Count")],
        [translation.gettext("Not Applied"), str(statistics_data['not_applied'])],
        [translation.gettext("Applied"), str(statistics_data['applied'])],
        [translation.gettext("Application Confirmed"), str(statistics_data['confirmed'])],
        [translation.gettext("Response Received"), str(statistics_data['response_received'])],
        [translation.gettext("Rejected"), str(statistics_data['rejected'])],
        [translation.gettext("Accepted"), str(statistics_data['accepted'])],
    ]
    
    status_table = Table(status_data, colWidths=[4*inch, 2.5*inch])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), CYRILLIC_FONT_BOLD),
        ('FONTNAME', (0, 1), (-1, -1), CYRILLIC_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(status_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Success rates
    story.append(Paragraph(translation.gettext("Success Rates"), heading_style))
    success_data = [
        [translation.gettext("Indicator"), translation.gettext("Value")],
        [translation.gettext("Success Rate"), f"{statistics_data['success_rate']}%"],
        [translation.gettext("Rejection Rate"), f"{statistics_data['rejection_rate']}%"],
    ]
    
    success_table = Table(success_data, colWidths=[3.5*inch, 3*inch])
    success_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), CYRILLIC_FONT_BOLD),
        ('FONTNAME', (0, 1), (-1, -1), CYRILLIC_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(success_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Time-based statistics
    story.append(Paragraph(translation.gettext("Time-based Statistics"), heading_style))
    
    # Create style for table text with smaller font size
    table_text_style = ParagraphStyle(
        'TableText',
        parent=normal_style,
        fontName=CYRILLIC_FONT,
        fontSize=8,
        leading=10,
        alignment=TA_CENTER
    )
    
    # Use Paragraph for headers so text can wrap
    time_data = [
        [
            Paragraph(translation.gettext("Period"), table_text_style),
            Paragraph(translation.gettext("Jobs Added"), table_text_style),
            Paragraph(translation.gettext("Resumes Submitted"), table_text_style),
            Paragraph(translation.gettext("Responses"), table_text_style),
            Paragraph(translation.gettext("Rejections"), table_text_style)
        ],
        [
            Paragraph(translation.gettext("Last Week"), table_text_style), 
            str(statistics_data['jobs_last_week']), 
            str(statistics_data['resumes_submitted_last_week']),
            str(statistics_data['responses_last_week']),
            str(statistics_data['rejections_last_week'])
        ],
        [
            Paragraph(translation.gettext("Last Month"), table_text_style), 
            str(statistics_data['jobs_last_month']), 
            str(statistics_data['resumes_submitted_last_month']),
            str(statistics_data['responses_last_month']),
            str(statistics_data['rejections_last_month'])
        ],
        [
            Paragraph(translation.gettext("Last Year"), table_text_style), 
            str(statistics_data.get('jobs_last_year', 0)), 
            str(statistics_data.get('resumes_submitted_last_year', 0)),
            str(statistics_data.get('responses_last_year', 0)),
            str(statistics_data.get('rejections_last_year', 0))
        ],
    ]
    
    # Increase column widths for long texts (especially for Russian and German)
    # Use wider columns for "Jobs Added" and "Resumes Submitted"
    # Total table width: 1.4 + 1.5 + 1.6 + 1.0 + 1.0 = 6.5 inches (fits A4)
    time_table = Table(time_data, colWidths=[1.4*inch, 1.5*inch, 1.6*inch, 1.0*inch, 1.0*inch])
    time_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # First column (Period) align to left
        ('FONTNAME', (0, 0), (-1, 0), CYRILLIC_FONT_BOLD),
        ('FONTNAME', (0, 1), (-1, -1), CYRILLIC_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment to center
    ]))
    story.append(time_table)
    
    # Top employers
    if statistics_data.get('top_employers'):
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(translation.gettext("Top Employers"), heading_style))
        employer_data = [[translation.gettext("#"), translation.gettext("Employer"), translation.gettext("Number of Jobs")]]
        for idx, employer in enumerate(statistics_data['top_employers'][:10], 1):
            employer_data.append([str(idx), employer['employer'], str(employer['count'])])
        
        employer_table = Table(employer_data, colWidths=[0.5*inch, 4*inch, 2*inch])
        employer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), CYRILLIC_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), CYRILLIC_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        story.append(employer_table)
    
    # Monthly statistics
    if statistics_data.get('monthly_stats'):
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(translation.gettext("Jobs Added by Month") + f" ({translation.gettext('Last 12 months')})", subheading_style))
        months = [stat['month'][5:] for stat in statistics_data['monthly_stats']]
        counts = [str(stat['count']) for stat in statistics_data['monthly_stats']]
        
        monthly_data = [months, counts]
        monthly_table = Table(monthly_data, colWidths=[0.5*inch] * len(months))
        monthly_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), CYRILLIC_FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), CYRILLIC_FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(monthly_table)
    
    # Footer
    story.append(Spacer(1, 0.4*inch))
    story.append(Paragraph(
        f"{translation.gettext('Generated')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        ParagraphStyle(
            'FooterStyle',
            parent=normal_style,
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
    ))
    
    # Restore previous language
    translation.activate(old_language)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_monthly_report_pdf(job_entries, year: int, month: int, username: str, language_code: str = 'en') -> BytesIO:
    """
    Generate PDF document with monthly job entries report
    
    Args:
        job_entries: QuerySet of JobEntry instances for the month
        year: Year for the report
        month: Month for the report (1-12)
        username: Username
        language_code: Language code (ru, en, de)
        
    Returns:
        BytesIO: Byte stream with PDF content
    """
    from django.utils import translation
    from datetime import datetime
    from .choices import STATUS_CHOICES
    
    # Activate language for translations
    old_language = translation.get_language()
    translation.activate(language_code)
    
    # Get month name
    month_names = {
        1: translation.gettext('January'), 2: translation.gettext('February'),
        3: translation.gettext('March'), 4: translation.gettext('April'),
        5: translation.gettext('May'), 6: translation.gettext('June'),
        7: translation.gettext('July'), 8: translation.gettext('August'),
        9: translation.gettext('September'), 10: translation.gettext('October'),
        11: translation.gettext('November'), 12: translation.gettext('December')
    }
    month_name = month_names.get(month, str(month))
    
    # Create status translation dict
    # STATUS_CHOICES contains tuples with lazy translation objects
    # When language is activated, lazy objects will be evaluated to translated strings
    status_dict = {}
    for key, label in STATUS_CHOICES:
        # Force evaluation of lazy translation object to get translated string
        status_dict[key] = str(label)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    story = []
    
    # Styles with Cyrillic support
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=CYRILLIC_FONT_BOLD,
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=CYRILLIC_FONT_BOLD,
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=CYRILLIC_FONT,
        fontSize=10,
        leading=12
    )
    
    table_text_style = ParagraphStyle(
        'TableText',
        parent=normal_style,
        fontName=CYRILLIC_FONT,
        fontSize=9,
        leading=11
    )
    
    # Title
    story.append(Paragraph(translation.gettext("Monthly Report"), title_style))
    story.append(Paragraph(f"{month_name} {year}", ParagraphStyle(
        'MonthStyle',
        parent=normal_style,
        fontSize=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#7f8c8d')
    )))
    story.append(Paragraph(f"{translation.gettext('User')}: {username}", ParagraphStyle(
        'UserStyle',
        parent=normal_style,
        fontSize=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#7f8c8d')
    )))
    story.append(Spacer(1, 0.3*inch))
    
    # Table data
    table_data = [[
        Paragraph(translation.gettext("Date"), table_text_style),
        Paragraph(translation.gettext("Employer"), table_text_style),
        Paragraph(translation.gettext("Job Title"), table_text_style),
        Paragraph(translation.gettext("Email"), table_text_style),
        Paragraph(translation.gettext("Result"), table_text_style),
        Paragraph(translation.gettext("Result Date"), table_text_style)
    ]]
    
    # Add job entries
    for job in job_entries:
        # First column: Application submission date
        # Try to get date from resume_submitted_date first, then from ResumeSubmissionStatus
        date_str = translation.gettext('Not specified')
        if job.resume_submitted_date:
            date_str = job.resume_submitted_date.strftime('%d.%m.%Y')
        else:
            # Try to get date from ResumeSubmissionStatus with status_type='resume_sent'
            try:
                resume_status = job.resume_statuses.filter(status_type='resume_sent').order_by('date_time').first()
                if resume_status:
                    date_str = resume_status.date_time.strftime('%d.%m.%Y')
                elif job.resume_submitted and job.created_at:
                    # Fallback to creation date if resume was submitted but no specific date
                    date_str = job.created_at.strftime('%d.%m.%Y')
            except Exception:
                # If there's any error accessing resume_statuses, use created_at as fallback
                if job.created_at:
                    date_str = job.created_at.strftime('%d.%m.%Y')
        
        employer = job.employer or translation.gettext('Not specified')
        job_title = job.job_title or translation.gettext('Not specified')
        email = job.contact_email or translation.gettext('Not specified')
        # Get translated status - status_dict already contains translated strings
        status_display = status_dict.get(job.status, translation.gettext(job.status))
        
        # Determine result date based on status
        # First try to get date from JobEntryHistory (most accurate), then ResumeSubmissionStatus, then model fields
        result_date_str = translation.gettext('Not specified')
        try:
            # First, try to get date from JobEntryHistory (most accurate)
            status_history = job.history.filter(field_name='status').order_by('-changed_at').first()
            if status_history:
                result_date_str = status_history.changed_at.strftime('%d.%m.%Y')
            else:
                # Fallback: Get the latest ResumeSubmissionStatus that matches the current status
                # Map JobEntry.status to possible ResumeSubmissionStatus.status_type values
                status_mapping = {
                    'rejected': ['rejection_received'],
                    'response_received': ['response_received'],
                    'interview_scheduled': ['interview_scheduled', 'another_interview_scheduled'],
                    'interview_passed': ['interview_passed'],
                    'documents_requested': ['documents_requested'],
                    'accepted': ['response_received'],  # Accepted is also a response
                    'confirmed': ['confirmation_received'],
                    'applied': ['resume_sent'],
                }
            
                status_types_to_find = status_mapping.get(job.status, [])
                if status_types_to_find:
                    latest_status = job.resume_statuses.filter(
                        status_type__in=status_types_to_find
                    ).order_by('-date_time').first()
                    if latest_status:
                        result_date_str = latest_status.date_time.strftime('%d.%m.%Y')
                
                # Fallback to old date fields if no ResumeSubmissionStatus found
                if result_date_str == translation.gettext('Not specified'):
                    if job.status == 'rejected' and job.rejection_date:
                        result_date_str = job.rejection_date.strftime('%d.%m.%Y')
                    elif job.status in ['response_received', 'accepted', 'interview_scheduled', 'interview_passed', 'documents_requested'] and job.response_date:
                        result_date_str = job.response_date.strftime('%d.%m.%Y')
                    elif job.status in ['interview_scheduled', 'interview_passed'] and job.interview_date:
                        result_date_str = job.interview_date.strftime('%d.%m.%Y')
                    elif job.status == 'confirmed' and job.confirmation_date:
                        result_date_str = job.confirmation_date.strftime('%d.%m.%Y')
                    elif job.status == 'applied' and job.resume_submitted_date:
                        result_date_str = job.resume_submitted_date.strftime('%d.%m.%Y')
        except Exception:
            # If there's any error, try JobEntryHistory first, then use old date fields as fallback
            try:
                status_history = job.history.filter(field_name='status').order_by('-changed_at').first()
                if status_history:
                    result_date_str = status_history.changed_at.strftime('%d.%m.%Y')
                elif job.status == 'rejected' and job.rejection_date:
                    result_date_str = job.rejection_date.strftime('%d.%m.%Y')
                elif job.status in ['response_received', 'accepted', 'interview_scheduled', 'interview_passed', 'documents_requested'] and job.response_date:
                    result_date_str = job.response_date.strftime('%d.%m.%Y')
                elif job.status in ['interview_scheduled', 'interview_passed'] and job.interview_date:
                    result_date_str = job.interview_date.strftime('%d.%m.%Y')
                elif job.status == 'confirmed' and job.confirmation_date:
                    result_date_str = job.confirmation_date.strftime('%d.%m.%Y')
                elif job.status == 'applied' and job.resume_submitted_date:
                    result_date_str = job.resume_submitted_date.strftime('%d.%m.%Y')
            except Exception:
                pass
        
        table_data.append([
            Paragraph(date_str, table_text_style),
            Paragraph(employer, table_text_style),
            Paragraph(job_title, table_text_style),
            Paragraph(email, table_text_style),
            Paragraph(status_display, table_text_style),
            Paragraph(result_date_str, table_text_style)
        ])
    
    # If no entries
    if not job_entries:
        table_data.append([
            Paragraph(translation.gettext('No entries for this month'), table_text_style),
            '', '', '', '', ''
        ])
    
    # Create table
    # Column widths for landscape A4: Date (1.2"), Employer (2"), Job Title (2.5"), Email (1.8"), Result (1.5"), Result Date (1.2")
    # Total width: ~10.2 inches (landscape A4 width is ~11.69 inches)
    table = Table(table_data, colWidths=[1.2*inch, 2*inch, 2.5*inch, 1.8*inch, 1.5*inch, 1.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Date column centered
        ('FONTNAME', (0, 0), (-1, 0), CYRILLIC_FONT_BOLD),
        ('FONTNAME', (0, 1), (-1, -1), CYRILLIC_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(table)
    
    # Footer
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(
        f"{translation.gettext('Generated')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        ParagraphStyle(
            'FooterStyle',
            parent=normal_style,
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
    ))
    
    # Restore previous language
    translation.activate(old_language)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

