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
