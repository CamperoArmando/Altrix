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

    # Campos de soporte para el bloqueo temporal de HU-08 (no forman parte
    # del diagrama entidad-relación original; se agregan como extensión
    # controlada, documentada aquí, para cumplir el criterio de aceptación
    # "tras 3 intentos fallidos la sesión se bloquea temporalmente").
    intentos_fallidos = db.Column(db.Integer, nullable=False, default=0)
    bloqueado_hasta = db.Column(db.DateTime, nullable=True)

    rol = db.relationship("Rol", back_populates="usuarios")
    ventas = db.relationship("Venta", back_populates="usuario")
    movimientos = db.relationship("MovimientoInventario", back_populates="usuario")

    def set_password(self, password_plano: str):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password_plano)

    def check_password(self, password_plano: str) -> bool:
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password_plano)

    def get_info(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol.nombre if self.rol else None,
            "activo": self.activo,
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None,
        }
