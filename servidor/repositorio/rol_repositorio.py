from modelo.rol import Rol


class RolRepositorio:
    def buscar_por_nombre(self, nombre: str):
        return Rol.query.filter_by(nombre=nombre).first()

    def listar(self):
        return Rol.query.order_by(Rol.id).all()
