
from repositorio.venta_repositorio import VentaRepositorio
from repositorio.producto_repositorio import ProductoRepositorio
from extensions import db  # Para manejar el commit/rollback en Postgres

venta_repo = VentaRepositorio()
producto_repo = ProductoRepositorio()

class VentaServicio:
    
    @staticmethod
    def procesar_venta(datos_venta, usuario_id):
        detalles = datos_venta.get('detalles', [])
        if not detalles:
            raise ValueError("La venta no contiene productos")

        total_venta = 0
        detalles_procesados = []

        # Bloque Try-Except para asegurar la integridad referencial manual
        try:
            for item in detalles:
                producto_id = item.get('producto_id')
                cantidad = item.get('cantidad')

                # 1. Buscar el producto en PostgreSQL
                producto = producto_repo.obtener_por_id(producto_id)
                if not producto:
                    raise ValueError(f"Producto con ID {producto_id} no encontrado")

                # 2. Validar disponibilidad de stock
                if producto.stock_actual < cantidad:
                    raise ValueError(f"Stock insuficiente para {producto.nombre}")

                # 3. Descontar el stock en la memoria de SQLAlchemy
                producto.stock_actual -= cantidad
                
                # 4. Calcular el subtotal
                subtotal = float(producto.precio) * cantidad
                total_venta += subtotal

                # 5. Preparar el sub-documento (detalle) para MongoDB
                detalles_procesados.append({
                    "producto_id": producto_id, # ID de Postgres
                    "nombre_producto": producto.nombre,
                    "cantidad": cantidad,
                    "precio_unitario": float(producto.precio),
                    "subtotal": subtotal
                })

            # 6. Guardar cambios de stock en PostgreSQL permanentemente
            db.session.commit()

            # 7. Armar el documento principal de la venta para MongoDB
            documento_venta = {
                "usuario_id": usuario_id, # ID string de MongoDB
                "total": total_venta,
                "estado": "completada",
                "detalles": detalles_procesados
            }

            # 8. Guardar la venta estructurada en MongoDB
            venta_creada = venta_repo.crear_venta(documento_venta)
            return venta_creada

        except Exception as e:
            # Si algo falla (ej. falta de stock de un producto intermedio), 
            # revertimos cualquier cambio pendiente en PostgreSQL
            db.session.rollback()
            raise e

from datetime import datetime
from extensions import db
from repositorio.venta_repositorio import VentaRepositorio
from repositorio.producto_repositorio import ProductoRepositorio
from modelo.venta import Venta
from modelo.detalle_venta import DetalleVenta
from modelo.movimiento_inventario import MovimientoInventario


class VentaServicio:
    def __init__(self):
        self.__venta_repo = VentaRepositorio()
        self.__producto_repo = ProductoRepositorio.get_instancia()

    def registrar(self, usuario_id: int, producto_id: int, cantidad: int):
        """
        HU-05: registra una venta con su detalle, descuenta el stock del
        producto y deja un movimiento de inventario (SALIDA) para
        trazabilidad. Todo en una sola transacción: si algo falla, no
        queda ni la venta ni el descuento de stock a medias.
        """
        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            return {"error": "Cantidad inválida"}, 400

        if cantidad <= 0:
            return {"error": "La cantidad debe ser mayor a cero"}, 400

        producto = self.__producto_repo.buscar(producto_id)
        if not producto:
            return {"error": "Producto no encontrado"}, 404

        if producto.get_cantidad() < cantidad:
            return {"error": "Stock insuficiente"}, 400

        precio_unitario = producto.precio
        subtotal = precio_unitario * cantidad

        venta = Venta(usuario_id=usuario_id, total=subtotal)
        detalle = DetalleVenta(
            producto_id=producto.id,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            subtotal=subtotal,
        )
        venta.detalles.append(detalle)

        producto.set_cantidad(producto.get_cantidad() - cantidad)

        movimiento = MovimientoInventario(
            producto_id=producto.id,
            usuario_id=usuario_id,
            tipo="SALIDA",
            cantidad=cantidad,
            motivo="Venta registrada",
        )

        db.session.add(venta)
        db.session.add(movimiento)
        db.session.commit()

        return {
            "mensaje": "Venta registrada correctamente",
            "venta_id": venta.id,
            "total": float(venta.total),
        }, 201

    def historial(self, fecha_desde: str = None, fecha_hasta: str = None, producto_id: int = None):
        """HU-09: historial de ventas, filtrable por rango de fechas y por producto."""
        desde_dt = self._parsear_fecha(fecha_desde)
        hasta_dt = self._parsear_fecha(fecha_hasta, fin_de_dia=True)

        try:
            producto_id = int(producto_id) if producto_id else None
        except (TypeError, ValueError):
            producto_id = None

        ventas = self.__venta_repo.listar(desde_dt, hasta_dt, producto_id)

        resultado = []
        for v in ventas:
            info = v.get_info()
            info["usuario_nombre"] = v.usuario.nombre if v.usuario else None
            info["detalles"] = []
            for d in v.detalles:
                detalle_info = d.get_info()
                detalle_info["producto_nombre"] = d.producto.nombre if d.producto else None
                info["detalles"].append(detalle_info)
            resultado.append(info)

        return resultado, 200

    @staticmethod
    def _parsear_fecha(valor: str, fin_de_dia: bool = False):
        if not valor:
            return None
        try:
            fecha = datetime.strptime(valor, "%Y-%m-%d")
            if fin_de_dia:
                fecha = fecha.replace(hour=23, minute=59, second=59)
            return fecha
        except ValueError:
            return None

