from flask import Blueprint, request, jsonify
from servicio.usuario_servicio import UsuarioServicio
from repositorio.rol_repositorio import RolRepositorio
from controlador.decoradores import requiere_rol

usuario_bp = Blueprint("usuario", __name__)
servicio = UsuarioServicio()
rol_repo = RolRepositorio()


@usuario_bp.route("/usuarios", methods=["GET"])
@requiere_rol("Administrador")
def listar():
    data, status = servicio.listar()
    return jsonify(data), status


@usuario_bp.route("/usuarios/<int:id>", methods=["GET"])
@requiere_rol("Administrador")
def consultar(id):
    data, status = servicio.consultar(id)
    return jsonify(data), status


@usuario_bp.route("/usuarios", methods=["POST"])
@requiere_rol("Administrador")
def alta():
    datos = request.get_json(silent=True) or {}
    data, status = servicio.alta(datos)
    return jsonify(data), status


@usuario_bp.route("/usuarios/<int:id>", methods=["PUT"])
@requiere_rol("Administrador")
def modificar(id):
    datos = request.get_json(silent=True) or {}
    data, status = servicio.modificar(id, datos)
    return jsonify(data), status


@usuario_bp.route("/usuarios/<int:id>/rol", methods=["PATCH"])
@requiere_rol("Administrador")
def asignar_rol(id):
    datos = request.get_json(silent=True) or {}
    data, status = servicio.asignar_rol(id, datos.get("rol", ""))
    return jsonify(data), status


@usuario_bp.route("/usuarios/<int:id>", methods=["DELETE"])
@requiere_rol("Administrador")
def baja(id):
    data, status = servicio.baja(id)
    return jsonify(data), status


@usuario_bp.route("/roles", methods=["GET"])
@requiere_rol("Administrador")
def listar_roles():
    return jsonify([r.get_info() for r in rol_repo.listar()]), 200
