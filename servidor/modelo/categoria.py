from extensions import db


class Categoria(db.Model):
    __tablename__ = "categoria"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    descripcion = db.Column(db.String(255), nullable=True)

    productos = db.relationship("Producto", back_populates="categoria")

    def get_info(self) -> dict:
        return {"id": self.id, "nombre": self.nombre, "descripcion": self.descripcion}
