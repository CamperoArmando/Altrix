from flask import Blueprint, request, jsonify
from servicio.auth_servicio import AuthServicio

auth_bp = Blueprint("auth", __name__)
servicio = AuthServicio()


@auth_bp.route("/login", methods=["POST"])
def login():
    datos = request.get_json() or {}
    data, status = servicio.login(datos.get("email"), datos.get("password"))
    return jsonify(data), status