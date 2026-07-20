from extensions import db
from repositorio.producto_repositorio import ProductoRepositorio
from repositorio.categoria_repositorio import CategoriaRepositorio
from modelo.producto import Producto


class ProductoServicio:
    def __init__(self):
        self.__repo = ProductoRepositorio.get_instancia()
        self.__categoria_repo = CategoriaRepositorio()

    def alta(self, datos: dict):
        try:
            if not str(datos.get("nombre", "")).strip():
                return {"error": "Datos inválidos"}, 400

            categoria = self.__categoria_repo.obtener_o_crear(str(datos["categoria"]))

            producto = Producto(
                nombre=str(datos["nombre"]),
                precio=float(datos["precio"]),
                cantidad_stock=int(datos["cantidad"]),
                categoria_id=categoria.id,
            )
            if not producto.es_valido():
                db.session.rollback()
                return {"error": "Datos inválidos"}, 400

            self.__repo.agregar(producto)
            return {"mensaje": "Producto agregado correctamente", "id": producto.get_id()}, 201
        except (KeyError, ValueError, TypeError):
            db.session.rollback()
            return {"error": "Datos inválidos"}, 400

    def baja(self, id: int):
        producto = self.__repo.buscar(id)
        if not producto:
            return {"error": "Producto no encontrado"}, 404
        self.__repo.eliminar(id)
        return {"mensaje": "Producto eliminado correctamente"}, 200

    def consultar(self, id: int):
        producto = self.__repo.buscar(id)
        if not producto:
            return {"error": "Producto no encontrado"}, 404
        return producto.get_info(), 200

    def listar(self):
        productos = self.__repo.listar()
        return [p.get_info() for p in productos], 200

    def modificar(self, id: int, datos: dict):
        producto = self.__repo.buscar(id)
        if not producto:
            return {"error": "Producto no encontrado"}, 404
        try:
            if "nombre" in datos:
                producto.set_nombre(str(datos["nombre"]))
            if "precio" in datos:
                producto.set_precio(float(datos["precio"]))
            if "cantidad" in datos:
                producto.set_cantidad(int(datos["cantidad"]))
            if "categoria" in datos:
                categoria = self.__categoria_repo.obtener_o_crear(str(datos["categoria"]))
                producto.set_categoria_id(categoria.id)
        except (ValueError, TypeError):
            db.session.rollback()
            return {"error": "Datos inválidos"}, 400

        if not producto.es_valido():
            db.session.rollback()
            return {"error": "Datos inválidos"}, 400

        self.__repo.actualizar(producto)
        return {"mensaje": "Producto modificado correctamente"}, 200

    def vender(self, id: int, cantidad: int):
        producto = self.__repo.buscar(id)
        if not producto:
            return {"error": "Producto no encontrado"}, 404
        if producto.get_cantidad() < cantidad:
            return {"error": "Stock insuficiente"}, 400
        producto.set_cantidad(producto.get_cantidad() - cantidad)
        self.__repo.actualizar(producto)
        return {"mensaje": "Venta realizada correctamente"}, 200
