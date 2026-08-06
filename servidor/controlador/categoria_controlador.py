from flask import Blueprint, request, jsonify
from servicio.categoria_servicio import CategoriaServicio
from controlador.decoradores import requiere_auth, requiere_rol

categoria_bp = Blueprint("categoria", __name__)
servicio = CategoriaServicio()


@categoria_bp.route("/categorias", methods=["GET"])
@requiere_auth
def listar():
    data, status = servicio.listar()
    return jsonify(data), status


@categoria_bp.route("/categorias/<int:id>", methods=["GET"])
@requiere_auth
def consultar(id):
    data, status = servicio.consultar(id)
    return jsonify(data), status


@categoria_bp.route("/categorias", methods=["POST"])
@requiere_rol("Administrador")
def alta():
    datos = request.get_json() or {}
    data, status = servicio.alta(datos)
    return jsonify(data), status


@categoria_bp.route("/categorias/<int:id>", methods=["PUT"])
@requiere_rol("Administrador")
def modificar(id):
    datos = request.get_json() or {}
    data, status = servicio.modificar(id, datos)
    return jsonify(data), status


@categoria_bp.route("/categorias/<int:id>", methods=["DELETE"])
@requiere_rol("Administrador")
def baja(id):
    data, status = servicio.baja(id)
    return jsonify(data), status
