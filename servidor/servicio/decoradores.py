from functools import wraps
import jwt
from flask import request, jsonify, current_app
from repositorio.usuario_repositorio import UsuarioRepositorio


def _obtener_token():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1]
    return None


def token_required(f):          # <- debe empezar en columna 0
    @wraps(f)
    def decorada(*args, **kwargs):
        ...
    return decorada


def rol_requerido(*roles_permitidos):   # <- debe empezar en columna 0
    def decorador(f):
        ...
    return decorador