
from extensions import mongo_db
from bson.objectid import ObjectId
from datetime import datetime

class UsuarioRepositorio:
    def __init__(self):
        # Referencia a la colección 'usuarios' en MongoDB
        self.coleccion = mongo_db.usuarios

    def obtener_por_email(self, email):
        return self.coleccion.find_one({"email": email})

    def obtener_por_id(self, usuario_id):
        try:
            return self.coleccion.find_one({"_id": ObjectId(usuario_id)})
        except:
            return None

    def crear_usuario(self, datos_usuario):
        # Asignamos la fecha de creación si no viene
        datos_usuario['fecha_creacion'] = datetime.utcnow()
        # Insertamos en Mongo
        resultado = self.coleccion.insert_one(datos_usuario)
        # Devolvemos el documento creado
        datos_usuario['_id'] = str(resultado.inserted_id)
        return datos_usuario

    def obtener_todos(self):
        usuarios = list(self.coleccion.find({}))
        # Convertir ObjectId a string para que sea serializable a JSON
        for usr in usuarios:
            usr['_id'] = str(usr['_id'])
        return usuarios

from extensions import db
from modelo.usuario import Usuario


class UsuarioRepositorio:
    def buscar_por_email(self, email: str):
        return Usuario.query.filter_by(email=email).first()

    def buscar_por_id(self, id: int):
        return Usuario.query.get(id)

    def agregar(self, usuario: Usuario):
        db.session.add(usuario)
        db.session.commit()

    def guardar_cambios(self):
        db.session.commit()

    def listar(self):
        return Usuario.query.order_by(Usuario.id).all()

    def actualizar(self):
        db.session.commit()

    def eliminar_logico(self, usuario: Usuario):
        """Baja lógica: se conserva el registro (ventas/movimientos ya
        asociados a este usuario no deben perder su referencia), pero
        deja de poder iniciar sesión ni aparecer como activo."""
        usuario.activo = False
        db.session.commit()

