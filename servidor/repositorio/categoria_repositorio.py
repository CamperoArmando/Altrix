from extensions import db
from modelo.categoria import Categoria


class CategoriaRepositorio:
    """
    Repositorio de Categoria. Se usa tanto como apoyo de ProductoRepositorio
    (resolver nombre -> id, creando la categoría si no existe) como para la
    gestión explícita de categorías de HU-06.
    """

    def buscar_por_nombre(self, nombre: str):
        return Categoria.query.filter_by(nombre=nombre).first()

    def buscar_por_id(self, id: int):
        return Categoria.query.get(id)

    def obtener_o_crear(self, nombre: str) -> Categoria:
        nombre = nombre.strip()
        categoria = self.buscar_por_nombre(nombre)
        if categoria is None:
            categoria = Categoria(nombre=nombre)
            db.session.add(categoria)
            db.session.flush()  # asigna el id sin cerrar la transacción
        return categoria

    def agregar(self, categoria: Categoria):
        db.session.add(categoria)
        db.session.commit()

    def listar(self):
        return Categoria.query.order_by(Categoria.nombre).all()

    def actualizar(self):
        db.session.commit()

    def eliminar(self, categoria: Categoria):
        db.session.delete(categoria)
        db.session.commit()

    def tiene_productos(self, categoria_id: int) -> bool:
        from modelo.producto import Producto
        return Producto.query.filter_by(categoria_id=categoria_id, activo=True).first() is not None
