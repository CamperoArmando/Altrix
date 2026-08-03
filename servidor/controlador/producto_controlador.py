from flask import Blueprint, request, jsonify
from servicio.producto_servicio import ProductoServicio
from controlador.decoradores import requiere_auth, requiere_rol

producto_bp = Blueprint("producto", __name__)
servicio = ProductoServicio()

# Lectura: cualquier usuario autenticado (Administrador o Vendedor)
@producto_bp.route("/productos", methods=["GET"])
@requiere_auth
def listar():
    data, status = servicio.listar()
    return jsonify(data), status

@producto_bp.route("/productos/<int:id>", methods=["GET"])
@requiere_auth
def consultar(id):
    data, status = servicio.consultar(id)
    return jsonify(data), status

# Escritura sobre el catálogo: solo Administrador
@producto_bp.route("/productos", methods=["POST"])
@requiere_rol("Administrador")
def alta():
    datos = request.get_json()
    data, status = servicio.alta(datos)
    return jsonify(data), status

@producto_bp.route("/productos/<int:id>", methods=["DELETE"])
@requiere_rol("Administrador")
def baja(id):
    data, status = servicio.baja(id)
    return jsonify(data), status

@producto_bp.route("/productos/<int:id>", methods=["PUT"])
@requiere_rol("Administrador")
def modificar(id):
    datos = request.get_json()
    data, status = servicio.modificar(id, datos)
    return jsonify(data), status
