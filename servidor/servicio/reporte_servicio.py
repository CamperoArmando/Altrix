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