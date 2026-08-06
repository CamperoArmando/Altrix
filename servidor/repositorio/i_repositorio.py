from abc import ABC, abstractmethod

class IRepositorio(ABC):

    @abstractmethod
    def agregar(self, producto):
        pass

    @abstractmethod
    def eliminar(self, id: int):
        pass

    @abstractmethod
    def buscar(self, id: int):
        pass

    @abstractmethod
    def listar(self):
        pass

    @abstractmethod
    def actualizar(self, producto):
        pass