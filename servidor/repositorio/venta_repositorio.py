from datetime import datetime
from extensions import db
from modelo.venta import Venta
from modelo.detalle_venta import DetalleVenta


class VentaRepositorio:
    def agregar(self, venta: Venta):
        db.session.add(venta)
        db.session.commit()

    def buscar_por_id(self, id: int):
        return Venta.query.get(id)

    def listar(self, fecha_desde: datetime = None, fecha_hasta: datetime = None, producto_id: int = None):
        query = Venta.query

        if producto_id:
            query = query.join(DetalleVenta).filter(DetalleVenta.producto_id == producto_id)
        if fecha_desde:
            query = query.filter(Venta.fecha >= fecha_desde)
        if fecha_hasta:
            query = query.filter(Venta.fecha <= fecha_hasta)

        return query.order_by(Venta.fecha.desc()).all()
