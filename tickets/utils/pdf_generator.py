import os
from datetime  import datetime
from reportlab.lib.pagesizes  import A4
from reportlab.lib            import colors
from reportlab.lib.units      import cm
from reportlab.platypus       import (SimpleDocTemplate, Table, TableStyle,
                                      Paragraph, Spacer, HRFlowable)
from reportlab.lib.styles     import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums      import TA_CENTER, TA_LEFT

TICKETS_DIR = 'tickets'
os.makedirs(TICKETS_DIR, exist_ok=True)

NAVY  = colors.HexColor('#0a2540')
GOLD  = colors.HexColor('#f5a623')
LIGHT = colors.HexColor('#f0f4f8')
CREAM = colors.HexColor('#fefce8')
GRAY  = colors.HexColor('#6b7280')
WHITE = colors.white
GREEN = colors.HexColor('#166534')
GLIGHT= colors.HexColor('#dcfce7')

def _style(name, **kw):
    s = ParagraphStyle(name, **kw)
    return s

def generate_ticket_pdf(booking, train, user):
    path = os.path.join(TICKETS_DIR, f"ticket_{booking['pnr']}.pdf")
    doc  = SimpleDocTemplate(path, pagesize=A4,
                             rightMargin=1.5*cm, leftMargin=1.5*cm,
                             topMargin=1.5*cm,   bottomMargin=1.5*cm)
    story = []

    # ── HEADER ──────────────────────────────────────────────────
    hdr   = _style('hdr',  fontSize=24, textColor=WHITE,     alignment=TA_CENTER, fontName='Helvetica-Bold')
    sub   = _style('sub',  fontSize=10, textColor=GOLD,      alignment=TA_CENTER, fontName='Helvetica')
    ht = Table([[Paragraph('🚆  RAILBOOK TICKET', hdr)],
                [Paragraph('Indian Railway Reservation System', sub)]],
               colWidths=[18*cm])
    ht.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,-1), NAVY),
        ('TOPPADDING',   (0,0),(-1, 0), 20),
        ('BOTTOMPADDING',(0,-1),(-1,-1),20),
        ('LEFTPADDING',  (0,0),(-1,-1), 16),
    ]))
    story.append(ht)
    story.append(Spacer(1, 0.4*cm))

    # ── PNR + STATUS ─────────────────────────────────────────────
    pnr_s = _style('pnr_s', fontSize=16, textColor=NAVY, alignment=TA_CENTER, fontName='Helvetica-Bold')
    sta_s = _style('sta_s', fontSize=12, textColor=GREEN,alignment=TA_CENTER, fontName='Helvetica-Bold')
    pt = Table([[Paragraph(f"PNR : {booking['pnr']}", pnr_s),
                 Paragraph(f"✅  {str(booking['status']).upper()}", sta_s)]],
               colWidths=[9*cm, 9*cm])
    pt.setStyle(TableStyle([
        ('BACKGROUND',  (0,0),(-1,-1), LIGHT),
        ('BOX',         (0,0),(-1,-1), 1.5, NAVY),
        ('ROWPADDING',  (0,0),(-1,-1), 10),
    ]))
    story.append(pt)
    story.append(Spacer(1, 0.4*cm))

    # ── TRAIN DETAILS ────────────────────────────────────────────
    lbl = _style('lbl', fontSize=8,  textColor=GRAY, fontName='Helvetica')
    val = _style('val', fontSize=11, textColor=NAVY, fontName='Helvetica-Bold')
    def cell(l, v):
        return [Paragraph(l, lbl), Paragraph(str(v), val)]

    td = [
        [cell('TRAIN NUMBER',  train['train_no']),
         cell('TRAIN NAME',    train['train_name']),
         cell('TYPE',          train['train_type'])],
        [cell('FROM',          train['from_station']),
         cell('TO',            train['to_station']),
         cell('JOURNEY DATE',  booking['journey_date'])],
        [cell('DEPARTURE',     train['departure']),
         cell('ARRIVAL',       train['arrival']),
         cell('SEAT(S)',        booking['seats'])],
    ]
    tt = Table(td, colWidths=[6*cm,6*cm,6*cm])
    tt.setStyle(TableStyle([
        ('GRID',       (0,0),(-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWPADDING', (0,0),(-1,-1), 8),
        ('BACKGROUND', (0,0),(-1, 0), LIGHT),
    ]))
    story.append(tt)
    story.append(Spacer(1, 0.4*cm))

    # ── PASSENGER ────────────────────────────────────────────────
    pd_ = [
        [cell('PASSENGER',  user['username']),
         cell('EMAIL',      user['email']),
         cell('TOTAL PAID', f"₹ {float(booking['total_price']):.2f}")],
    ]
    payt = Table(pd_, colWidths=[6*cm,6*cm,6*cm])
    payt.setStyle(TableStyle([
        ('GRID',       (0,0),(-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWPADDING', (0,0),(-1,-1), 8),
        ('BACKGROUND', (0,0),(-1,-1), CREAM),
    ]))
    story.append(payt)
    story.append(Spacer(1, 0.4*cm))

    # ── FOOTER ────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=1, color=NAVY))
    story.append(Spacer(1, 0.2*cm))
    ft = _style('ft', fontSize=8, textColor=GRAY, alignment=TA_CENTER)
    story.append(Paragraph(
        'Computer-generated ticket — no signature required. '
        'Carry a valid government photo ID during travel.', ft))
    story.append(Paragraph(f"Booked on: {booking['booked_at']}", ft))

    doc.build(story)
    return path