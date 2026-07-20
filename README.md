# Proyecto Altrix — Sistema de Inventario y Ventas

Ampliación del CRUD de productos original: ahora persiste en **PostgreSQL**
siguiendo el diagrama entidad-relación del documento del proyecto (7 tablas:
`rol`, `usuario`, `categoria`, `producto`, `venta`, `detalle_venta`,
`movimiento_inventario`).

## Estado actual (Sprint 1, en progreso)

Implementadas con persistencia real en base de datos:

- **HU-01** — Alta de producto (`POST /productos`)
- **HU-02** — Listado de productos (`GET /productos`)
- **HU-03** — Modificar producto (`PUT /productos/<id>`)
- **HU-04** — Eliminar producto — baja lógica vía columna `activo` (`DELETE /productos/<id>`)

También se conserva `vender` (`PUT /productos/<id>/vender`), ya funcional en
el proyecto original, ahora respaldado por la base de datos.

Pendientes para el resto del Sprint 1: HU-07 (ya cubierta por las
validaciones existentes), HU-08 (login) y refuerzo de HU-10. Sprint 2:
HU-05 (venta con historial en `venta`/`detalle_venta`), HU-06 (gestión de
categorías), HU-09 (historial de ventas).

## Cómo levantar el proyecto (Docker — recomendado)

Requiere Docker y Docker Compose.

```bash
docker compose up --build
```

Esto levanta 3 contenedores:

| Servicio   | Puerto | Descripción                              |
|------------|--------|-------------------------------------------|
| `db`       | 5432   | PostgreSQL 16, con volumen persistente     |
| `servidor` | 5000   | API Flask (crea las tablas automáticamente al iniciar) |
| `cliente`  | 3000   | Interfaz web Node/Express/EJS              |

Abre **http://localhost:3000** para usar la interfaz.

Al iniciar, el servidor:
1. Se conecta a PostgreSQL.
2. Crea las tablas si no existen (`db.create_all()`).
3. Siembra los roles base `Administrador` y `Vendedor`.

Los datos persisten en el volumen `altrix_db_data` aunque se reinicien o
recreen los contenedores (`docker compose down` sin `-v`).

## Cómo correrlo sin Docker (desarrollo local)

Necesitas una instancia de PostgreSQL accesible y Python 3.12 + Node 20.

```bash
# Servidor
cd servidor
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Ajusta servidor/.env con los datos de tu PostgreSQL local
python controlador/app.py

# Cliente (en otra terminal)
cd cliente
npm install
node app/index.js
```

## Notas de diseño

- **Categorías**: el formulario conserva un campo de texto libre por
  compatibilidad con la interfaz existente; el servidor resuelve ese
  nombre contra la tabla `categoria` (la crea si no existe). La gestión
  completa de categorías (alta/edición explícita) llega en HU-06.
- **Eliminar producto (HU-04)** es una baja lógica (`activo = false`), no
  un `DELETE` físico, para no romper la integridad referencial cuando
  Sprint 2 añada el historial de ventas.
- **IDs de producto**: ahora los genera la base de datos (`SERIAL`); el
  formulario de alta ya no pide un ID manual.
