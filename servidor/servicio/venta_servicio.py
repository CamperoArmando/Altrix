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