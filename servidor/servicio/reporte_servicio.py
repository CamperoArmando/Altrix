
from repositorio.venta_repositorio import VentaRepositorio

venta_repo = VentaRepositorio()

class ReporteServicio:

    @staticmethod
    def obtener_datos_ventas():
        """
        Obtiene el historial completo de ventas para los reportes PDF/Excel.
        """
        ventas_mongo = venta_repo.obtener_todas()
        datos_limpios = []

        for venta in ventas_mongo:
            datos_limpios.append({
                "id_venta": venta.get('_id'),
                "fecha": venta.get('fecha'),
                "total": venta.get('total'),
                "estado": venta.get('estado'),
                "cantidad_articulos": sum(item.get('cantidad', 0) for item in venta.get('detalles', []))
            })
            
        return datos_limpios

    @staticmethod
    def obtener_productos_mas_vendidos():
        """
        Agrupa los productos vendidos iterando sobre los documentos de MongoDB.
        """
        ventas_mongo = venta_repo.obtener_todas()
        conteo_productos = {}

        # Recorremos cada venta y sus detalles embebidos
        for venta in ventas_mongo:
            # Solo contamos ventas completadas
            if venta.get('estado') != 'completada':
                continue
                
            for detalle in venta.get('detalles', []):
                prod_id = str(detalle.get('producto_id'))
                
                if prod_id not in conteo_productos:
                    conteo_productos[prod_id] = {
                        "producto_id": prod_id,
                        "nombre": detalle.get('nombre_producto'),
                        "cantidad_vendida": 0,
                        "ingreso_generado": 0.0
                    }
                
                # Acumulamos las métricas
                conteo_productos[prod_id]['cantidad_vendida'] += detalle.get('cantidad', 0)
                conteo_productos[prod_id]['ingreso_generado'] += detalle.get('subtotal', 0.0)

        # Convertimos el diccionario a lista y lo ordenamos de mayor a menor cantidad
        lista_ranking = list(conteo_productos.values())
        lista_ranking.sort(key=lambda x: x['cantidad_vendida'], reverse=True)

        return lista_ranking

from datetime import datetime
from sqlalchemy import func

from extensions import db
from modelo.venta import Venta
from modelo.detalle_venta import DetalleVenta
from modelo.producto import Producto
from repositorio.venta_repositorio import VentaRepositorio


class ReporteServicio:
    """
    CU5 - Consultar reportes. Prepara los datos (ya agregados y listos
    para tabular) que consumen los generadores de PDF/Excel. No conoce
    nada de formato de archivo: esa responsabilidad vive en
    reporte_pdf.py / reporte_excel.py, para no mezclar "qué datos son"
    con "cómo se ven en el archivo".
    """

    def __init__(self):
        self.__venta_repo = VentaRepositorio()

    @staticmethod
    def parsear_fecha(valor: str, fin_de_dia: bool = False):
        if not valor:
            return None
        try:
            fecha = datetime.strptime(valor, "%Y-%m-%d")
            if fin_de_dia:
                fecha = fecha.replace(hour=23, minute=59, second=59)
            return fecha
        except ValueError:
            return None

    def ventas_por_periodo(self, desde_str: str = None, hasta_str: str = None):
        desde = self.parsear_fecha(desde_str)
        hasta = self.parsear_fecha(hasta_str, fin_de_dia=True)

        ventas = self.__venta_repo.listar(desde, hasta)

        filas = []
        total_general = 0
        for v in ventas:
            for d in v.detalles:
                filas.append({
                    "fecha": v.fecha.strftime("%Y-%m-%d %H:%M"),
                    "venta_id": v.id,
                    "vendedor": v.usuario.nombre if v.usuario else "—",
                    "producto": d.producto.nombre if d.producto else "—",
                    "cantidad": d.cantidad,
                    "precio_unitario": float(d.precio_unitario),
                    "subtotal": float(d.subtotal),
                })
                total_general += float(d.subtotal)

        return {
            "desde": desde_str or "(sin límite)",
            "hasta": hasta_str or "(sin límite)",
            "filas": filas,
            "total_general": round(total_general, 2),
            "num_ventas": len(ventas),
        }

    def productos_mas_vendidos(self, desde_str: str = None, hasta_str: str = None, limite: int = 10):
        desde = self.parsear_fecha(desde_str)
        hasta = self.parsear_fecha(hasta_str, fin_de_dia=True)

        try:
            limite = max(1, int(limite))
        except (TypeError, ValueError):
            limite = 10

        query = (
            db.session.query(
                Producto.id,
                Producto.nombre,
                func.sum(DetalleVenta.cantidad).label("unidades_vendidas"),
                func.sum(DetalleVenta.subtotal).label("total_vendido"),
            )
            .join(DetalleVenta, DetalleVenta.producto_id == Producto.id)
            .join(Venta, Venta.id == DetalleVenta.venta_id)
        )

        if desde:
            query = query.filter(Venta.fecha >= desde)
        if hasta:
            query = query.filter(Venta.fecha <= hasta)

        resultados = (
            query.group_by(Producto.id, Producto.nombre)
            .order_by(func.sum(DetalleVenta.cantidad).desc())
            .limit(limite)
            .all()
        )

        filas = [
            {
                "producto_id": r.id,
                "producto": r.nombre,
                "unidades_vendidas": int(r.unidades_vendidas),
                "total_vendido": float(r.total_vendido),
            }
            for r in resultados
        ]

        return {
            "desde": desde_str or "(sin límite)",
            "hasta": hasta_str or "(sin límite)",
            "filas": filas,
        }

