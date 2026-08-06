from flask import Blueprint, request, jsonify
from servicio.auth_servicio import AuthServicio
from controlador.decoradores import requiere_auth
from repositorio.usuario_repositorio import UsuarioRepositorio

auth_bp = Blueprint("auth", __name__)
servicio = AuthServicio()
usuario_repo = UsuarioRepositorio()


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    datos = request.get_json(silent=True) or {}
    data, status = servicio.login(datos.get("email", ""), datos.get("password", ""))
    return jsonify(data), status


@auth_bp.route("/auth/me", methods=["GET"])
@requiere_auth
def me():
    from flask import g
    usuario = usuario_repo.buscar_por_id(g.usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(usuario.get_info()), 200
