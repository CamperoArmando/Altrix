from repositorio.usuario_repositorio import UsuarioRepositorio
from repositorio.rol_repositorio import RolRepositorio
from modelo.usuario import Usuario


class UsuarioServicio:
    def __init__(self):
        self.__repo = UsuarioRepositorio()
        self.__rol_repo = RolRepositorio()

    def listar(self):
        usuarios = self.__repo.listar()
        return [u.get_info() for u in usuarios], 200

    def consultar(self, id: int):
        usuario = self.__repo.buscar_por_id(id)
        if not usuario:
            return {"error": "Usuario no encontrado"}, 404
        return usuario.get_info(), 200

    def alta(self, datos: dict):
        nombre = str(datos.get("nombre", "")).strip()
        email = str(datos.get("email", "")).strip().lower()
        password = datos.get("password", "")
        rol_nombre = str(datos.get("rol", "")).strip()

        if not nombre or not email or not password or not rol_nombre:
            return {"error": "nombre, email, password y rol son obligatorios"}, 400

        if self.__repo.buscar_por_email(email):
            return {"error": "Ya existe un usuario con ese email"}, 409

        rol = self.__rol_repo.buscar_por_nombre(rol_nombre)
        if not rol:
            return {"error": f"El rol '{rol_nombre}' no existe"}, 400

        usuario = Usuario(nombre=nombre, email=email, rol_id=rol.id)
        usuario.set_password(password)
        self.__repo.agregar(usuario)
        return {"mensaje": "Usuario creado correctamente", "id": usuario.id}, 201

    def modificar(self, id: int, datos: dict):
        usuario = self.__repo.buscar_por_id(id)
        if not usuario:
            return {"error": "Usuario no encontrado"}, 404

        if "nombre" in datos:
            nombre = str(datos["nombre"]).strip()
            if not nombre:
                return {"error": "El nombre no puede quedar vacío"}, 400
            usuario.nombre = nombre

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not email:
                return {"error": "El email no puede quedar vacío"}, 400
            existente = self.__repo.buscar_por_email(email)
            if existente and existente.id != usuario.id:
                return {"error": "Ya existe otro usuario con ese email"}, 409
            usuario.email = email

        if "password" in datos and datos["password"]:
            usuario.set_password(str(datos["password"]))

        if "activo" in datos:
            usuario.activo = bool(datos["activo"])

        self.__repo.actualizar()
        return {"mensaje": "Usuario modificado correctamente"}, 200

    def asignar_rol(self, id: int, rol_nombre: str):
        usuario = self.__repo.buscar_por_id(id)
        if not usuario:
            return {"error": "Usuario no encontrado"}, 404

        rol = self.__rol_repo.buscar_por_nombre(str(rol_nombre).strip())
        if not rol:
            return {"error": f"El rol '{rol_nombre}' no existe"}, 400

        usuario.rol_id = rol.id
        self.__repo.actualizar()
        return {"mensaje": f"Rol actualizado a '{rol.nombre}'", "usuario": usuario.get_info()}, 200

    def baja(self, id: int):
        usuario = self.__repo.buscar_por_id(id)
        if not usuario:
            return {"error": "Usuario no encontrado"}, 404
        self.__repo.eliminar_logico(usuario)
        return {"mensaje": "Usuario desactivado correctamente"}, 200
