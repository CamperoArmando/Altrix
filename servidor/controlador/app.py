import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db
from extensions import db, init_mongo

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
from controlador.categoria_controlador import categoria_bp
from controlador.venta_controlador import venta_bp
from controlador.usuario_controlador import usuario_bp
from controlador.reporte_controlador import reporte_bp
app.register_blueprint(producto_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(categoria_bp)
app.register_blueprint(venta_bp)
app.register_blueprint(usuario_bp)
app.register_blueprint(reporte_bp)


def create_app():
    # ... inicialización de Flask ...
    db.init_app(app)
    init_mongo(app) # <--- Añadir esta línea
    return app

def _sembrar_roles():
    """Crea los roles base (Administrador, Vendedor, Consultor) si no existen."""
    for nombre in ("Administrador", "Vendedor", "Consultor"):
        if not Rol.query.filter_by(nombre=nombre).first():
            db.session.add(Rol(nombre=nombre))
    db.session.commit()


def _sembrar_admin():
    """
    Crea un usuario Administrador inicial si todavía no existe ningún
    usuario en el sistema. Sin esto, nadie podría iniciar sesión la
    primera vez que se levanta el proyecto.

    Credenciales por defecto (cámbialas en cuanto puedas iniciar sesión):
      email:    admin@altrix.com
      password: Admin123!
    """
    if Usuario.query.count() > 0:
        return
    rol_admin = Rol.query.filter_by(nombre="Administrador").first()
    admin = Usuario(nombre="Administrador", email="admin@altrix.com", rol_id=rol_admin.id)
    admin.set_password("Admin123!")
    db.session.add(admin)
    db.session.commit()
    print(">> Usuario Administrador inicial creado: admin@altrix.com / Admin123!")


from seed_datos import sembrar_productos  # noqa: E402

with app.app_context():
    db.create_all()
    _sembrar_roles()
    _sembrar_admin()
    sembrar_productos()

if __name__ == "__main__":
    # IMPORTANTE: debug=True activa el auto-reloader de Werkzeug, que vigila
    # el filesystem y puede reiniciar el proceso a mitad de una sesión
    # (p.ej. por escritura de .pyc, journaling de la DB, etc.). Dentro de un
    # contenedor esto es especialmente inestable: si el reinicio cae justo
    # entre el login y la siguiente petición, el cliente ve el token
    # "rechazado de inmediato". threaded=True permite además atender las
    # peticiones concurrentes que dispara el cliente Node (Promise.all).
    app.run(debug=False, port=5000, host="0.0.0.0", threaded=True)
