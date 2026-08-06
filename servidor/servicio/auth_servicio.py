from repositorio.usuario_repositorio import UsuarioRepositorio
from werkzeug.security import check_password_hash
import jwt
from datetime import datetime, timedelta
import os

usuario_repo = UsuarioRepositorio()
# Asegúrate de tener una variable de entorno para tu clave secreta
SECRET_KEY = os.environ.get('SECRET_KEY', 'super_secreto_altrix')

class AuthServicio:
    
    @staticmethod
    def login(email, password):
        # 1. Buscar usuario en MongoDB como diccionario
        usuario = usuario_repo.obtener_por_email(email)
        
        if not usuario:
            raise ValueError("Usuario no encontrado")

        # 2. Verificar la contraseña (asumiendo que las guardas hasheadas con werkzeug)
        if not check_password_hash(usuario.get('password'), password):
            raise ValueError("Credenciales inválidas")

        # 3. Generar el Token JWT usando el _id de Mongo convertido a string
        payload = {
            'sub': str(usuario['_id']),
            'email': usuario.get('email'),
            'rol': usuario.get('rol_id'), # O 'rol' dependiendo de cómo lo guardes en Mongo
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        
        # 4. Retornar el token y los datos básicos del usuario
        return {
            "token": token,
            "usuario": {
                "id": str(usuario['_id']),
                "nombre": usuario.get('nombre'),
                "email": usuario.get('email'),
                "rol": usuario.get('rol_id')
            }
        }

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

