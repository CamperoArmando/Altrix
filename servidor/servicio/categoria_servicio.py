from extensions import db
from repositorio.categoria_repositorio import CategoriaRepositorio
from modelo.categoria import Categoria


class CategoriaServicio:
    def __init__(self):
        self.__repo = CategoriaRepositorio()

    def alta(self, datos: dict):
        nombre = str(datos.get("nombre", "")).strip()
        if not nombre:
            return {"error": "El nombre de la categoría es obligatorio"}, 400

        if self.__repo.buscar_por_nombre(nombre):
            return {"error": "Ya existe una categoría con ese nombre"}, 409

        categoria = Categoria(nombre=nombre, descripcion=datos.get("descripcion"))
        self.__repo.agregar(categoria)
        return {"mensaje": "Categoría creada correctamente", "id": categoria.id}, 201

    def listar(self):
        categorias = self.__repo.listar()
        return [c.get_info() for c in categorias], 200

    def consultar(self, id: int):
        categoria = self.__repo.buscar_por_id(id)
        if not categoria:
            return {"error": "Categoría no encontrada"}, 404
        return categoria.get_info(), 200

    def modificar(self, id: int, datos: dict):
        categoria = self.__repo.buscar_por_id(id)
        if not categoria:
            return {"error": "Categoría no encontrada"}, 404

        nuevo_nombre = str(datos.get("nombre", categoria.nombre)).strip()
        if not nuevo_nombre:
            return {"error": "El nombre de la categoría es obligatorio"}, 400

        existente = self.__repo.buscar_por_nombre(nuevo_nombre)
        if existente and existente.id != categoria.id:
            return {"error": "Ya existe otra categoría con ese nombre"}, 409

        categoria.nombre = nuevo_nombre
        if "descripcion" in datos:
            categoria.descripcion = datos["descripcion"]

        self.__repo.actualizar()
        return {"mensaje": "Categoría modificada correctamente"}, 200

    def baja(self, id: int):
        categoria = self.__repo.buscar_por_id(id)
        if not categoria:
            return {"error": "Categoría no encontrada"}, 404

        if self.__repo.tiene_productos(id):
            return {"error": "No se puede eliminar: hay productos activos en esta categoría"}, 409

        self.__repo.eliminar(categoria)
        return {"mensaje": "Categoría eliminada correctamente"}, 200
