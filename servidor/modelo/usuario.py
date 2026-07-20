from datetime import datetime
from extensions import db


class Usuario(db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey("rol.id"), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    rol = db.relationship("Rol", back_populates="usuarios")
    ventas = db.relationship("Venta", back_populates="usuario")
    movimientos = db.relationship("MovimientoInventario", back_populates="usuario")

    def get_info(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol.nombre if self.rol else None,
            "activo": self.activo,
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None,
        }
