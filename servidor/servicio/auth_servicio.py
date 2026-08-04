from datetime import datetime, timedelta
import jwt
from flask import current_app

from extensions import db
from repositorio.usuario_repositorio import UsuarioRepositorio
from repositorio.rol_repositorio import RolRepositorio
from modelo.usuario import Usuario


class AuthServicio:
    MAX_INTENTOS = 3
    MINUTOS_BLOQUEO = 5

    def __init__(self):
        self.__usuario_repo = UsuarioRepositorio()
        self.__rol_repo = RolRepositorio()

    def login(self, email: str, password: str):
        if not email or not password:
            return {"error": "Email y contraseña son obligatorios"}, 400

        usuario = self.__usuario_repo.buscar_por_email(email.strip().lower())
        if not usuario or not usuario.activo:
            return {"error": "Credenciales inválidas"}, 401

        ahora = datetime.utcnow()

        if usuario.bloqueado_hasta and usuario.bloqueado_hasta > ahora:
            restante_min = max(1, int((usuario.bloqueado_hasta - ahora).total_seconds() // 60) + 1)
            return {
                "error": f"Cuenta bloqueada temporalmente por demasiados intentos fallidos. "
                         f"Intenta de nuevo en {restante_min} minuto(s)."
            }, 423

        if not usuario.check_password(password):
            usuario.intentos_fallidos = (usuario.intentos_fallidos or 0) + 1
            if usuario.intentos_fallidos >= self.MAX_INTENTOS:
                usuario.bloqueado_hasta = ahora + timedelta(minutes=self.MINUTOS_BLOQUEO)
                usuario.intentos_fallidos = 0
                self.__usuario_repo.guardar_cambios()
                return {
                    "error": f"Demasiados intentos fallidos. Cuenta bloqueada por "
                             f"{self.MINUTOS_BLOQUEO} minutos."
                }, 423
            self.__usuario_repo.guardar_cambios()
            intentos_restantes = self.MAX_INTENTOS - usuario.intentos_fallidos
            return {"error": f"Credenciales inválidas. Te quedan {intentos_restantes} intento(s)."}, 401

        # Login correcto: se reinician los contadores de bloqueo
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        self.__usuario_repo.guardar_cambios()

        token = self._generar_token(usuario)
        return {
            "token": token,
            "usuario": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "email": usuario.email,
                "rol": usuario.rol.nombre,
            },
        }, 200

    def _generar_token(self, usuario: Usuario) -> str:
        payload = {
            "sub": str(usuario.id),
            "nombre": usuario.nombre,
            "rol": usuario.rol.nombre,
            "exp": datetime.utcnow() + timedelta(hours=current_app.config["JWT_EXP_HORAS"]),
        }
        return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

    def registrar(self, nombre: str, email: str, password: str, rol_nombre: str = "Vendedor"):
        """Alta de usuario. Sin endpoint público expuesto por ahora: se usa
        para el sembrado inicial del Administrador (ver app.py)."""
        if self.__usuario_repo.buscar_por_email(email.strip().lower()):
            return {"error": "Ya existe un usuario con ese email"}, 409

        rol = self.__rol_repo.buscar_por_nombre(rol_nombre)
        if not rol:
            return {"error": f"El rol '{rol_nombre}' no existe"}, 400

        usuario = Usuario(nombre=nombre, email=email.strip().lower(), rol_id=rol.id)
        usuario.set_password(password)
        self.__usuario_repo.agregar(usuario)
        return {"mensaje": "Usuario creado correctamente", "id": usuario.id}, 201
