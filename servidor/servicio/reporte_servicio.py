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
