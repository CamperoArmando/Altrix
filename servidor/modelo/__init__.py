# Importa todos los modelos para que SQLAlchemy los registre en los metadatos
# antes de llamar a db.create_all(). El orden importa poco porque las FKs
# se resuelven por nombre de tabla, no por orden de import.
from modelo.rol import Rol
from modelo.usuario import Usuario
from modelo.categoria import Categoria
from modelo.producto import Producto
from modelo.venta import Venta
from modelo.detalle_venta import DetalleVenta
from modelo.movimiento_inventario import MovimientoInventario

__all__ = [
    "Rol",
    "Usuario",
    "Categoria",
    "Producto",
    "Venta",
    "DetalleVenta",
    "MovimientoInventario",
]
