from datetime import datetime
from extensions import db


class MovimientoInventario(db.Model):
    __tablename__ = "movimiento_inventario"
    __table_args__ = (
        db.CheckConstraint("tipo IN ('ENTRADA', 'SALIDA')", name="ck_movimiento_tipo_valido"),
        db.CheckConstraint("cantidad > 0", name="ck_movimiento_cantidad_positiva"),
    )

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("producto.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(150), nullable=True)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    producto = db.relationship("Producto", back_populates="movimientos")
    usuario = db.relationship("Usuario", back_populates="movimientos")

    def get_info(self) -> dict:
        return {
            "id": self.id,
            "producto_id": self.producto_id,
            "usuario_id": self.usuario_id,
            "tipo": self.tipo,
            "cantidad": self.cantidad,
            "motivo": self.motivo,
            "fecha": self.fecha.isoformat() if self.fecha else None,
        }
