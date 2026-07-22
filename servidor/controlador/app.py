# servidor/controlador/app.py
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
from modelo.usuario import Usuario  # noqa: E402

from controlador.producto_controlador import producto_bp
from controlador.auth_controlador import auth_bp
app.register_blueprint(producto_bp)
app.register_blueprint(auth_bp)


def _sembrar_roles():
    """Crea los roles base (Administrador, Vendedor) si no existen."""
    for nombre in ("Administrador", "Vendedor"):
        if not Rol.query.filter_by(nombre=nombre).first():
            db.session.add(Rol(nombre=nombre))
    db.session.commit()


def _sembrar_admin():
    """
    Crea un usuario Administrador inicial si no hay ninguno, para poder
    iniciar sesión desde el primer arranque (HU-08). Credenciales
    configurables por variables de entorno para no dejar nada fijo en código.
    """
    admin_email = os.getenv("ADMIN_EMAIL", "admin@altrix.local")
    admin_password = os.getenv("ADMIN_PASSWORD", "Admin123!")

    if Usuario.query.filter_by(email=admin_email).first():
        return

    rol_admin = Rol.query.filter_by(nombre="Administrador").first()
    usuario = Usuario(nombre="Administrador", email=admin_email, rol_id=rol_admin.id)
    usuario.set_password(admin_password)
    db.session.add(usuario)
    db.session.commit()


with app.app_context():
    db.create_all()
    _sembrar_roles()
    _sembrar_admin()

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")