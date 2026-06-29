# -*- coding: utf-8 -*-
# Copyright © 2026 Invisioned Marketing inc. All Rights Reserved.
"""
PDF Forge Phial v1.0
=====================
Converts the Master System Spec to a high-status PDF artifact.
Utilizes reportlab for sovereign document generation.
"""

from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def forge_pdf(source_md: str, output_pdf: str):
    doc = SimpleDocTemplate(output_pdf, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    styles.add(ParagraphStyle(name='SovereignTitle', parent=styles['Title'], fontSize=24, spaceAfter=20, textColor='#000b1e'))
    styles.add(ParagraphStyle(name='SovereignHeader', parent=styles['Heading1'], fontSize=18, spaceBefore=15, spaceAfter=10, textColor='#000b1e'))
    styles.add(ParagraphStyle(name='SovereignCopyright', fontSize=8, alignment=TA_CENTER, textColor='#888888'))

    story = []
    
    try:
        content = Path(source_md).read_text(encoding='utf-8')
    except Exception as e:
        print(f"ERROR READING SOURCE: {e}")
        return

    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 12))
            continue
            
        if line.startswith('# '):
            story.append(Paragraph(line[2:], styles['SovereignTitle']))
        elif line.startswith('## '):
            story.append(Paragraph(line[3:], styles['SovereignHeader']))
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], styles['Heading2']))
        elif line.startswith('|') or line.startswith('```') or line.startswith('- '):
            # Preformatted or List text
            story.append(Paragraph(f"<i>{line}</i>", styles['Normal']))
        elif line.startswith('<!--'):
            continue # Skip comments
        else:
            story.append(Paragraph(line, styles['Normal']))

    # Add Footer
    story.append(Spacer(1, 48))
    story.append(Paragraph("Copyright © 2026 Invisioned Marketing inc. All Rights Reserved.", styles['SovereignCopyright']))

    doc.build(story)
    print(f"PDF FORGED: {output_pdf}")

if __name__ == "__main__":
    forge_pdf("docs/SEPTEM_REGNA/L7_ETHEREAL/MASTER_SYSTEM_SPEC.md", "docs/CAMELOT_OS_v400_SYSTEM_SPEC.pdf")
