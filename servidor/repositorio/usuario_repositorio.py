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