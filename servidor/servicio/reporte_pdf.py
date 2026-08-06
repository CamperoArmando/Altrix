import os
from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recursos", "logo.png")

_estilos = getSampleStyleSheet()
_titulo = ParagraphStyle("TituloReporte", parent=_estilos["Heading1"], textColor=colors.HexColor("#1e3a8a"))
_subtitulo = ParagraphStyle("Subtitulo", parent=_estilos["Normal"], textColor=colors.HexColor("#475569"))


def _encabezado(titulo: str, subtitulo: str):
    elementos = []
    if os.path.exists(LOGO_PATH):
        elementos.append(Image(LOGO_PATH, width=45 * mm, height=13.5 * mm))
    elementos.append(Spacer(1, 10))
    elementos.append(Paragraph(titulo, _titulo))
    elementos.append(Paragraph(subtitulo, _subtitulo))
    elementos.append(Spacer(1, 14))
    return elementos


def _estilo_tabla(num_columnas):
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT") if num_columnas > 2 else ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ])


def generar_pdf_ventas(datos: dict) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=20 * mm, bottomMargin=18 * mm)

    subtitulo = f"Ventas del {datos['desde']} al {datos['hasta']} · generado {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    elementos = _encabezado("Reporte de ventas", subtitulo)

    encabezados = ["Fecha", "Venta", "Vendedor", "Producto", "Cant.", "P. Unit.", "Subtotal"]
    filas = [encabezados]
    for f in datos["filas"]:
        filas.append([
            f["fecha"], str(f["venta_id"]), f["vendedor"], f["producto"],
            str(f["cantidad"]), f"${f['precio_unitario']:.2f}", f"${f['subtotal']:.2f}",
        ])

    if len(filas) == 1:
        elementos.append(Paragraph("No hay ventas registradas en este periodo.", _estilos["Normal"]))
    else:
        tabla = Table(filas, repeatRows=1)
        tabla.setStyle(_estilo_tabla(len(encabezados)))
        elementos.append(tabla)
        elementos.append(Spacer(1, 14))
        resumen = (f"<b>Total de ventas:</b> {datos['num_ventas']} &nbsp;&nbsp; "
                   f"<b>Monto total:</b> ${datos['total_general']:.2f}")
        elementos.append(Paragraph(resumen, _estilos["Normal"]))

    doc.build(elementos)
    buffer.seek(0)
    return buffer


def generar_pdf_mas_vendidos(datos: dict) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=20 * mm, bottomMargin=18 * mm)

    subtitulo = f"Periodo {datos['desde']} al {datos['hasta']} · generado {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    elementos = _encabezado("Productos más vendidos", subtitulo)

    encabezados = ["#", "Producto", "Unidades vendidas", "Total vendido"]
    filas = [encabezados]
    for i, f in enumerate(datos["filas"], start=1):
        filas.append([str(i), f["producto"], str(f["unidades_vendidas"]), f"${f['total_vendido']:.2f}"])

    if len(filas) == 1:
        elementos.append(Paragraph("No hay ventas registradas en este periodo.", _estilos["Normal"]))
    else:
        tabla = Table(filas, repeatRows=1, colWidths=[25 * mm, 75 * mm, 40 * mm, 40 * mm])
        tabla.setStyle(_estilo_tabla(len(encabezados)))
        elementos.append(tabla)

    doc.build(elementos)
    buffer.seek(0)
    return buffer
