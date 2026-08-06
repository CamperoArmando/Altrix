from functools import wraps
import jwt
from flask import request, jsonify, current_app, g


def _autenticar():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, (jsonify({"error": "No autenticado"}), 401)

    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None, (jsonify({"error": "Sesión expirada, vuelve a iniciar sesión"}), 401)
    except jwt.InvalidTokenError:
        return None, (jsonify({"error": "Token inválido"}), 401)

    return payload, None


def requiere_auth(f):
    """Exige un JWT válido, sin importar el rol."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        payload, error = _autenticar()
        if error:
            return error
        g.usuario_id = int(payload["sub"])
        g.usuario_rol = payload["rol"]
        return f(*args, **kwargs)
    return wrapper


def requiere_rol(*roles_permitidos):
    """Exige un JWT válido Y que el rol del usuario esté en roles_permitidos."""
    def decorador(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            payload, error = _autenticar()
            if error:
                return error
            if payload["rol"] not in roles_permitidos:
                return jsonify({"error": "No tienes permisos para esta acción"}), 403
            g.usuario_id = int(payload["sub"])
            g.usuario_rol = payload["rol"]
            return f(*args, **kwargs)
        return wrapper
    return decorador
