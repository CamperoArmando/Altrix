from extensions import db


class Rol(db.Model):
    __tablename__ = "rol"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), nullable=False, unique=True)

    usuarios = db.relationship("Usuario", back_populates="rol")

    def get_info(self) -> dict:
        return {"id": self.id, "nombre": self.nombre}
