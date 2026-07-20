from extensions import db


class DetalleVenta(db.Model):
    __tablename__ = "detalle_venta"
    __table_args__ = (
        db.CheckConstraint("cantidad > 0", name="ck_detalle_cantidad_positiva"),
    )

    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey("venta.id", ondelete="CASCADE"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("producto.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    venta = db.relationship("Venta", back_populates="detalles")
    producto = db.relationship("Producto", back_populates="detalles_venta")

    def get_info(self) -> dict:
        return {
            "id": self.id,
            "venta_id": self.venta_id,
            "producto_id": self.producto_id,
            "cantidad": self.cantidad,
            "precio_unitario": float(self.precio_unitario),
            "subtotal": float(self.subtotal),
        }
