from extensions import db
from modelo.categoria import Categoria


class CategoriaRepositorio:
    """
    Repositorio simple para Categoria. Por ahora solo se usa como apoyo
    de ProductoRepositorio (resolver nombre -> id, creando la categoría
    si no existe). La gestión completa de categorías (HU-06) se
    implementará en el Sprint 2.
    """

    def buscar_por_nombre(self, nombre: str):
        return Categoria.query.filter_by(nombre=nombre).first()

    def obtener_o_crear(self, nombre: str) -> Categoria:
        nombre = nombre.strip()
        categoria = self.buscar_por_nombre(nombre)
        if categoria is None:
            categoria = Categoria(nombre=nombre)
            db.session.add(categoria)
            db.session.flush()  # asigna el id sin cerrar la transacción
        return categoria
