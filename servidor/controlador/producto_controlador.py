

@producto_bp.route("/productos", methods=["POST"])
def alta():
    datos = request.get_json()
    data, status = servicio.alta(datos)
    return jsonify(data), status

@producto_bp.route("/productos/<int:id>", methods=["DELETE"])
def baja(id):
    data, status = servicio.baja(id)
    return jsonify(data), status

@producto_bp.route("/productos/<int:id>", methods=["PUT"])
def modificar(id):
    datos = request.get_json()
    data, status = servicio.modificar(id, datos)
    return jsonify(data), status

@producto_bp.route("/productos/<int:id>/vender", methods=["PUT"])
def vender(id):
    datos = request.get_json()
    cantidad = datos.get("cantidad", 0)
    data, status = servicio.vender(id, cantidad)
    return jsonify(data), status