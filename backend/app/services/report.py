"""PDF water usage report for a field, built with reportlab."""

import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.field import Field
from app.models.field_crop import FieldCrop


def build_field_report_pdf(field: Field, field_crop: FieldCrop, recommendation: dict, savings: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, title=f"AquaSense Report - {field.name}")
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("AquaSense Water Usage Report", styles["Title"]))
    elements.append(Paragraph(f"Field: {field.name}", styles["Heading2"]))
    elements.append(
        Paragraph(
            f"Crop: {field_crop.crop.name} &middot; Planted: {field_crop.planting_date} &middot; "
            f"Soil: {field.soil_type.replace('_', ' ')} &middot; Irrigation: {field.irrigation_method}",
            styles["Normal"],
        )
    )
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Today's Recommendation", styles["Heading2"]))
    rec_table = Table(
        [
            ["Date", recommendation["date"]],
            ["ET0 (mm)", f"{recommendation['et0_mm']:.2f}"],
            ["ETc (mm)", f"{recommendation['etc_mm']:.2f}"],
            ["Growth stage", recommendation["growth_stage"]],
            ["Soil water depletion (mm)", f"{recommendation['depletion_mm']:.1f}"],
            ["Needs irrigation", "Yes" if recommendation["needs_irrigation"] else "No"],
            ["Recommended depth (gross, mm)", f"{recommendation['gross_depth_mm']:.1f}"],
            ["Estimated duration (hours)", f"{recommendation['duration_hours']:.1f}"],
        ],
        colWidths=[2.5 * inch, 3 * inch],
    )
    rec_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    elements.append(rec_table)
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Water Savings Summary", styles["Heading2"]))
    savings_table = Table(
        [
            ["Metric", "AquaSense", "Fixed Schedule"],
            ["Total water applied (mm)", f"{savings['aquasense_total_mm']:.0f}", f"{savings['fixed_schedule_total_mm']:.0f}"],
            ["Irrigation events", str(savings["aquasense_events"]), str(savings["fixed_schedule_events"])],
        ],
        colWidths=[2.2 * inch, 1.6 * inch, 1.7 * inch],
    )
    savings_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f8cd1")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    elements.append(savings_table)
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(
        Paragraph(
            f"<b>{savings['percent_water_saved']:.0f}% less water</b> applied over the simulated "
            f"{savings['days_simulated']}-day window, compared to a fixed {savings['fixed_schedule_interval_days']}"
            f"-day irrigation schedule.",
            styles["Normal"],
        )
    )

    doc.build(elements)
    return buffer.getvalue()
