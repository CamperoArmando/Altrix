import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

db.init_app(app)

# Los modelos deben importarse (después de crear `db`) para que
# SQLAlchemy los registre antes de crear las tablas.
import modelo  # noqa: E402  (import intencionalmente después de db.init_app)
from modelo.rol import Rol  # noqa: E402

from controlador.producto_controlador import producto_bp
app.register_blueprint(producto_bp)


def _sembrar_roles():
    """Crea los roles base (Administrador, Vendedor) si no existen."""
    for nombre in ("Administrador", "Vendedor"):
        if not Rol.query.filter_by(nombre=nombre).first():
            db.session.add(Rol(nombre=nombre))
    db.session.commit()


with app.app_context():
    db.create_all()
    _sembrar_roles()

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
