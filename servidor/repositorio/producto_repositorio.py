from repositorio.i_repositorio import IRepositorio
from modelo.producto import Producto
from extensions import db


class ProductoRepositorio(IRepositorio):
    """
    Repositorio de Producto respaldado por la base de datos relacional
    (PostgreSQL vía SQLAlchemy). Reemplaza la lista en memoria original.

    Se conserva el patrón Singleton para no romper la forma en que
    ProductoServicio obtiene la instancia (get_instancia()), aunque ya
    no cumple ninguna función de almacenamiento: el estado real vive
    en la base de datos, no en el objeto Python.
    """
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia

    @classmethod
    def get_instancia(cls):
        if cls._instancia is None:
            cls._instancia = ProductoRepositorio()
        return cls._instancia

    def agregar(self, producto: Producto):
        db.session.add(producto)
        db.session.commit()

    def eliminar(self, id: int):
        """
        Baja lógica: en vez de borrar la fila (que rompería la integridad
        referencial con futuras ventas), se marca activo = False, tal como
        contempla el campo 'activo' del diagrama entidad-relación.
        """
        producto = self.buscar(id)
        if producto:
            producto.activo = False
            db.session.commit()

    def buscar(self, id: int):
        return Producto.query.filter_by(id=id, activo=True).first()

    def listar(self):
        return Producto.query.filter_by(activo=True).order_by(Producto.id).all()

    def actualizar(self, producto: Producto):
        # El objeto ya está adherido a la sesión (viene de buscar()),
        # por lo que solo hace falta confirmar los cambios.
        db.session.commit()
        return True
