from flask import Blueprint, request, jsonify, g
from servicio.venta_servicio import VentaServicio
from controlador.decoradores import requiere_rol

venta_bp = Blueprint("venta", __name__)
servicio = VentaServicio()


# Registrar una venta: Administrador o Vendedor
@venta_bp.route("/ventas", methods=["POST"])
@requiere_rol("Administrador", "Vendedor")
def registrar():
    datos = request.get_json() or {}
    data, status = servicio.registrar(
        usuario_id=g.usuario_id,
        producto_id=datos.get("producto_id"),
        cantidad=datos.get("cantidad", 0),
    )
    return jsonify(data), status


# Historial de ventas (HU-09): solo Administrador
@venta_bp.route("/ventas", methods=["GET"])
@requiere_rol("Administrador")
def historial():
    data, status = servicio.historial(
        fecha_desde=request.args.get("desde"),
        fecha_hasta=request.args.get("hasta"),
        producto_id=request.args.get("producto_id"),
    )
    return jsonify(data), status
