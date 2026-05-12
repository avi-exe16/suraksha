from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import io


def generate_str_report(transaction: dict) -> bytes:
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'title',
        parent=styles['Heading1'],
        fontSize=16,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        'subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=20,
    )

    section_style = ParagraphStyle(
        'section',
        parent=styles['Heading2'],
        fontSize=12,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1e40af'),
        spaceBefore=16,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        'normal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6,
    )

    risk_score = transaction.get('anomaly_score', 0)
    risk_level = 'HIGH' if risk_score >= 0.8 else 'MEDIUM' if risk_score >= 0.5 else 'LOW'

    elements = []

    elements.append(Paragraph('SUSPICIOUS TRANSACTION REPORT', title_style))
    elements.append(Paragraph('Financial Intelligence Unit — India (FIU-IND) Format', subtitle_style))

    meta_data = [
        ['Report Reference', f"STR-{transaction.get('txn_id', 'N/A')}-{datetime.now().strftime('%Y%m%d')}"],
        ['Generated On', datetime.now().strftime('%d %B %Y, %I:%M %p')],
        ['Reporting Entity', 'Canara Bank — SuRaksha Fraud Detection System'],
        ['Risk Level', risk_level],
        ['Anomaly Score', f"{(risk_score * 100):.1f}%"],
    ]

    meta_table = Table(meta_data, colWidths=[5*cm, 12*cm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.white]),
    ]))
    elements.append(meta_table)

    elements.append(Paragraph('1. Transaction Information', section_style))

    txn_data = [
        ['Field', 'Value'],
        ['Transaction ID', transaction.get('txn_id', 'N/A')],
        ['User ID', transaction.get('user_id', 'N/A')],
        ['Transaction Amount', f"INR {transaction.get('amount', 0):,.2f}"],
        ['Transaction City', transaction.get('city', 'N/A')],
        ['Merchant Category', transaction.get('merchant_category', 'N/A')],
        ['Transaction Time', str(transaction.get('timestamp', 'N/A'))],
        ['Device ID', str(transaction.get('device_id', 'N/A'))[:32] + '...'],
    ]

    txn_table = Table(txn_data, colWidths=[6*cm, 11*cm])
    txn_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f1f5f9')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
    ]))
    elements.append(txn_table)

    elements.append(Paragraph('2. Behavioral Anomaly Indicators', section_style))

    indicators = [
        ['Indicator', 'Value', 'Status'],
        ['Distance from Last Transaction', f"{transaction.get('km_from_last_txn', 0):.1f} km", 'ALERT' if transaction.get('km_from_last_txn', 0) > 500 else 'NORMAL'],
        ['Impossible Speed Detected', 'YES' if transaction.get('impossible_speed', 0) else 'NO', 'ALERT' if transaction.get('impossible_speed', 0) else 'NORMAL'],
        ['New Device Used', 'YES' if transaction.get('is_new_device', 0) else 'NO', 'ALERT' if transaction.get('is_new_device', 0) else 'NORMAL'],
        ['Night Transaction', 'YES' if transaction.get('is_night', 0) else 'NO', 'FLAG' if transaction.get('is_night', 0) else 'NORMAL'],
        ['Amount vs User Average', f"{(transaction.get('amount_vs_user_avg', 1) * 100):.0f}%", 'ALERT' if transaction.get('amount_vs_user_avg', 1) > 3 else 'NORMAL'],
        ['Transactions in Last 24hr', str(transaction.get('txn_count_24hr', 0)), 'FLAG' if transaction.get('txn_count_24hr', 0) > 5 else 'NORMAL'],
    ]

    ind_table = Table(indicators, colWidths=[7*cm, 5*cm, 5*cm])
    ind_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f1f5f9')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
    ]))
    elements.append(ind_table)

    elements.append(Paragraph('3. System Recommendation', section_style))

    if risk_level == 'HIGH':
        recommendation = 'BLOCK TRANSACTION. Anomaly score exceeds high-risk threshold of 80%. Immediate investigation required. Transaction has been automatically frozen pending review by compliance officer.'
    elif risk_level == 'MEDIUM':
        recommendation = 'STEP-UP AUTHENTICATION REQUIRED. Anomaly score exceeds medium-risk threshold of 50%. Customer must verify identity via OTP or biometric before transaction proceeds.'
    else:
        recommendation = 'APPROVE WITH MONITORING. Anomaly score is within acceptable range. Transaction approved. Continued behavioral monitoring active.'

    elements.append(Paragraph(recommendation, normal_style))
    elements.append(Spacer(1, 16))

    elements.append(Paragraph('4. Declaration', section_style))
    elements.append(Paragraph(
        'This report has been automatically generated by the SuRaksha Fraud Detection System in accordance with the Prevention of Money Laundering Act (PMLA) 2002 and the Digital Personal Data Protection Act (DPDP) 2023. The anomaly detection model used is an Isolation Forest ensemble with a ROC-AUC score of 0.9826.',
        normal_style
    ))

    elements.append(Spacer(1, 24))
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')} | SuRaksha v1.0.0 | Canara Bank Internal Use Only",
        ParagraphStyle('footer', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#94a3b8'))
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()