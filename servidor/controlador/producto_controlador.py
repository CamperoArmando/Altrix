# servidor/controlador/producto_controlador.py
from flask import Blueprint, request, jsonify
from servicio.producto_servicio import ProductoServicio
from servicio.decoradores import token_required, rol_requerido

producto_bp = Blueprint("producto", __name__)
servicio = ProductoServicio()


@producto_bp.route("/productos", methods=["GET"])
@token_required
def listar():
    data, status = servicio.listar()
    return jsonify(data), status


@producto_bp.route("/productos/<int:id>", methods=["GET"])
@token_required
def consultar(id):
    data, status = servicio.consultar(id)
    return jsonify(data), status


@producto_bp.route("/productos", methods=["POST"])
@rol_requerido("Administrador")
def alta():
    datos = request.get_json()
    data, status = servicio.alta(datos)
    return jsonify(data), status


@producto_bp.route("/productos/<int:id>", methods=["DELETE"])
@rol_requerido("Administrador")
def baja(id):
    data, status = servicio.baja(id)
    return jsonify(data), status


@producto_bp.route("/productos/<int:id>", methods=["PUT"])
@rol_requerido("Administrador")
def modificar(id):
    datos = request.get_json()
    data, status = servicio.modificar(id, datos)
    return jsonify(data), status


@producto_bp.route("/productos/<int:id>/vender", methods=["PUT"])
@token_required
def vender(id):
    datos = request.get_json()
    cantidad = datos.get("cantidad", 0)
    data, status = servicio.vender(id, cantidad)
    return jsonify(data), status