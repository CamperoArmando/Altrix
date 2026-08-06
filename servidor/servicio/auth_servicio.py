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