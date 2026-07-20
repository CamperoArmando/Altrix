from datetime import datetime
from extensions import db


class Venta(db.Model):
    __tablename__ = "venta"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    usuario = db.relationship("Usuario", back_populates="ventas")
    detalles = db.relationship(
        "DetalleVenta", back_populates="venta", cascade="all, delete-orphan"
    )

    def get_info(self) -> dict:
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "total": float(self.total),
        }
