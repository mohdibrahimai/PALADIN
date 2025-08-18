"""PDF report generation for PALADIN.

This module provides a function to generate a proof‑carrying answer
card in PDF format.  The report summarises the question, answer,
evidence graph and verification status.  It uses reportlab's platypus
framework to build the PDF.
"""

from __future__ import annotations

from typing import Dict, Any, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import json


def _flatten_evidence_nodes(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [n for n in graph.get("nodes", []) if n.get("type") == "evidence"]


def generate_report(path: str, question: str, result: Dict[str, Any]) -> None:
    """Create a PDF answer card at ``path`` summarising the PALADIN output."""
    doc = SimpleDocTemplate(path, pagesize=letter)
    styles = getSampleStyleSheet()
    story: List[Any] = []
    title_style = styles["Title"]
    normal = styles["BodyText"]
    bold = ParagraphStyle(name="Bold", parent=normal, fontName="Helvetica-Bold")
    # Title
    story.append(Paragraph("Proof‑Carrying Answer Card", title_style))
    story.append(Spacer(1, 12))
    # Question and answer
    story.append(Paragraph("<b>Question:</b> " + question, normal))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Answer:</b> " + result["answer"], normal))
    story.append(Spacer(1, 12))
    # Validity
    validity_text = "PASS" if result["valid"] else "FAIL"
    validity_colour = colors.green if result["valid"] else colors.red
    story.append(Paragraph(f"<b>Proof validity:</b> <font color='{validity_colour.hexval}'>{validity_text}</font>", normal))
    story.append(Spacer(1, 12))
    # Evidence table
    evidence_nodes = _flatten_evidence_nodes(result["graph"])
    if evidence_nodes:
        table_data = [["Node ID", "URL", "Span"]]
        for n in evidence_nodes:
            table_data.append([n.get("id", ""), n.get("url", ""), n.get("span", "")])
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ])
        table = Table(table_data, colWidths=[60, 140, 300])
        table.setStyle(table_style)
        story.append(Paragraph("<b>Evidence nodes:</b>", normal))
        story.append(table)
        story.append(Spacer(1, 12))
    # Details
    story.append(Paragraph("<b>Verification details:</b>", normal))
    details_json = result.get("details", {})
    details_str = json.dumps(details_json, indent=2)
    story.append(Paragraph(f"<pre>{details_str}</pre>", ParagraphStyle(name="Code", parent=normal, fontName="Courier", fontSize=8)))
    doc.build(story)