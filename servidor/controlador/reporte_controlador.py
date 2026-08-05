from flask import Blueprint, request, send_file, jsonify

from servicio.reporte_servicio import ReporteServicio
from servicio.reporte_pdf import generar_pdf_ventas, generar_pdf_mas_vendidos
from servicio.reporte_excel import generar_excel_ventas, generar_excel_mas_vendidos
from controlador.decoradores import requiere_rol

reporte_bp = Blueprint("reporte", __name__)
servicio = ReporteServicio()

# CU5: lo usa el Consultor, pero el Administrador administra "todas las
# funcionalidades además de las asignadas" -> también puede consultarlos.
ROLES_REPORTES = ("Administrador", "Consultor")


def _responder_archivo(buffer, nombre_archivo: str, formato: str):
    if formato == "excel":
        return send_file(
            buffer,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=f"{nombre_archivo}.xlsx",
        )
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{nombre_archivo}.pdf",
    )


@reporte_bp.route("/reportes/ventas", methods=["GET"])
@requiere_rol(*ROLES_REPORTES)
def reporte_ventas():
    formato = request.args.get("formato", "pdf").lower()
    if formato not in ("pdf", "excel"):
        return jsonify({"error": "formato debe ser 'pdf' o 'excel'"}), 400

    datos = servicio.ventas_por_periodo(
        desde_str=request.args.get("desde"),
        hasta_str=request.args.get("hasta"),
    )

    buffer = generar_excel_ventas(datos) if formato == "excel" else generar_pdf_ventas(datos)
    return _responder_archivo(buffer, "reporte_ventas", formato)


@reporte_bp.route("/reportes/productos-mas-vendidos", methods=["GET"])
@requiere_rol(*ROLES_REPORTES)
def reporte_mas_vendidos():
    formato = request.args.get("formato", "pdf").lower()
    if formato not in ("pdf", "excel"):
        return jsonify({"error": "formato debe ser 'pdf' o 'excel'"}), 400

    datos = servicio.productos_mas_vendidos(
        desde_str=request.args.get("desde"),
        hasta_str=request.args.get("hasta"),
        limite=request.args.get("limite", 10),
    )

    buffer = generar_excel_mas_vendidos(datos) if formato == "excel" else generar_pdf_mas_vendidos(datos)
    return _responder_archivo(buffer, "reporte_productos_mas_vendidos", formato)
