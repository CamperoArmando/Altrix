from datetime import datetime
from extensions import db


class Producto(db.Model):
    __tablename__ = "producto"
    __table_args__ = (
        db.CheckConstraint("precio > 0", name="ck_producto_precio_positivo"),
        db.CheckConstraint("cantidad_stock >= 0", name="ck_producto_stock_no_negativo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    cantidad_stock = db.Column(db.Integer, nullable=False, default=0)
    stock_minimo = db.Column(db.Integer, nullable=False, default=5)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    categoria = db.relationship("Categoria", back_populates="productos")
    detalles_venta = db.relationship("DetalleVenta", back_populates="producto")
    movimientos = db.relationship("MovimientoInventario", back_populates="producto")

    # ---- Getters (se conserva la misma interfaz que el modelo original) ----
    def get_id(self):
        return self.id

    def get_nombre(self):
        return self.nombre

    def get_precio(self):
        return float(self.precio)

    def get_cantidad(self):
        return self.cantidad_stock

    def get_categoria(self):
        return self.categoria.nombre if self.categoria else None

    def get_categoria_id(self):
        return self.categoria_id

    # ---- Setters ----
    def set_nombre(self, nombre: str):
        self.nombre = nombre

    def set_precio(self, precio: float):
        self.precio = precio

    def set_cantidad(self, cantidad: int):
        self.cantidad_stock = cantidad

    def set_categoria_id(self, categoria_id: int):
        self.categoria_id = categoria_id

    # ---- Métodos del diagrama original ----
    def get_info(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "precio": self.get_precio(),
            "cantidad": self.cantidad_stock,
            "categoria": self.get_categoria(),
            "stock_minimo": self.stock_minimo,
            "activo": self.activo,
        }

    def es_valido(self) -> bool:
        return (
            bool(self.nombre and self.nombre.strip() != "") and
            self.precio is not None and float(self.precio) > 0 and
            self.cantidad_stock is not None and self.cantidad_stock >= 0
        )
