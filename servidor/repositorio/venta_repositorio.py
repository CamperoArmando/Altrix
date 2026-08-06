
from extensions import mongo_db
from bson.objectid import ObjectId
from datetime import datetime

class VentaRepositorio:
    def __init__(self):
        # Referencia a la colección 'ventas' en MongoDB
        self.coleccion = mongo_db.ventas

    def crear_venta(self, datos_venta):
        # Insertar fecha de registro automáticamente
        datos_venta['fecha'] = datetime.utcnow()
        
        # Insertar el documento (la venta y sus detalles embebidos) en MongoDB
        resultado = self.coleccion.insert_one(datos_venta)
        
        # Devolver el documento con su nuevo ID convertido a string
        datos_venta['_id'] = str(resultado.inserted_id)
        return datos_venta

    def obtener_todas(self):
        ventas = list(self.coleccion.find({}))
        # Convertir ObjectId a string para la respuesta JSON
        for venta in ventas:
            venta['_id'] = str(venta['_id'])
        return ventas

    def obtener_por_id(self, venta_id):
        try:
            venta = self.coleccion.find_one({"_id": ObjectId(venta_id)})
            if venta:
                venta['_id'] = str(venta['_id'])
            return venta
        except:
            return None

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

