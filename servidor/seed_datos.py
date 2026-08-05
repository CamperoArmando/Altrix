"""
Seed de datos de catálogo para cumplir el requisito del proyecto final:
"Los productos deberán ... cargar al menos 200 productos para venta".

Se ejecuta automáticamente al levantar el servidor (ver app.py), y es
idempotente: si ya existen suficientes productos activos, no hace nada.
"""
import random

from extensions import db
from modelo.producto import Producto
from repositorio.categoria_repositorio import CategoriaRepositorio

MINIMO_PRODUCTOS = 200

# categoría -> (lista de nombres base, rango de precio)
CATALOGO = {
    "Electrónica": (
        ["Audífonos Bluetooth", "Cargador USB-C", "Cable HDMI", "Mouse inalámbrico",
         "Teclado mecánico", "Bocina portátil", "Power bank 10000mAh", "Webcam HD",
         "Hub USB 4 puertos", "Memoria USB 64GB", "Disco SSD 512GB", "Adaptador Wi-Fi",
         "Soporte para laptop", "Micrófono USB", "Monitor 24\"", "Base enfriadora laptop",
         "Regulador de voltaje", "Extensión eléctrica", "Foco inteligente", "Cámara de seguridad"],
        (150, 3500),
    ),
    "Ropa": (
        ["Playera algodón", "Sudadera con capucha", "Pantalón de mezclilla", "Chamarra ligera",
         "Short deportivo", "Camisa formal", "Vestido casual", "Chaleco", "Pants deportivo",
         "Gorra", "Bufanda", "Guantes de invierno", "Calcetines (paquete 3)", "Cinturón de piel",
         "Playera polo", "Falda", "Blusa manga larga", "Traje de baño", "Pijama", "Boxers (paquete 3)"],
        (99, 899),
    ),
    "Hogar": (
        ["Juego de sábanas", "Almohada viscoelástica", "Cortina blackout", "Set de toallas",
         "Organizador de closet", "Lámpara de mesa", "Tapete decorativo", "Set de vasos",
         "Juego de sartenes", "Licuadora", "Plancha de vapor", "Aspiradora de mano",
         "Difusor de aromas", "Reloj de pared", "Cesto para ropa", "Set de cubiertos",
         "Termo de acero inoxidable", "Tabla para picar", "Escurridor de trastes", "Bote de basura"],
        (120, 2200),
    ),
    "Alimentos": (
        ["Café molido 500g", "Té orgánico caja 20", "Miel de abeja 500ml", "Pasta integral 500g",
         "Aceite de oliva 500ml", "Granola artesanal 400g", "Chocolate amargo 100g", "Nueces mixtas 250g",
         "Salsa picante 200ml", "Cereal integral 300g", "Galletas integrales", "Jugo natural 1L",
         "Agua mineral 600ml (pack 6)", "Especias mixtas", "Vinagre balsámico 250ml",
         "Mermelada artesanal 300g", "Barra energética (caja 6)", "Café en grano 1kg",
         "Endulzante natural 200g", "Avena en hojuelas 500g"],
        (35, 450),
    ),
    "Juguetes": (
        ["Rompecabezas 500 piezas", "Set de bloques de construcción", "Peluche mediano",
         "Carro a control remoto", "Muñeca articulada", "Juego de mesa familiar", "Pelota deportiva",
         "Set de plastilina", "Kit de ciencia para niños", "Cometa", "Yo-yo", "Set de cartas",
         "Dinosaurio de juguete", "Cocina de juguete", "Set de pintura infantil",
         "Patineta pequeña", "Robot de juguete", "Set de té de juguete", "Bicicleta infantil",
         "Trompo"],
        (89, 1899),
    ),
    "Papelería": (
        ["Cuaderno profesional", "Set de plumas", "Mochila escolar", "Calculadora científica",
         "Set de colores (24)", "Carpeta de argollas", "Resaltadores (set 5)", "Tijeras escolares",
         "Pegamento en barra", "Regla de 30cm", "Sacapuntas", "Marcadores para pizarrón",
         "Post-it (paquete)", "Grapadora", "Clips (caja)", "Folder tamaño carta (paquete)",
         "Lápices HB (caja 12)", "Borrador blanco", "Cinta adhesiva", "Agenda anual"],
        (25, 650),
    ),
    "Deportes": (
        ["Tapete de yoga", "Mancuernas 5kg (par)", "Cuerda para saltar", "Balón de fútbol",
         "Guantes de boxeo", "Banda de resistencia (set)", "Botella deportiva 1L", "Casco para bicicleta",
         "Rodilleras deportivas", "Silbato de árbitro", "Muñequeras deportivas", "Bolsa deportiva",
         "Raqueta de tenis", "Red de voleibol portátil", "Rodillo de espuma", "Guantes de ciclismo",
         "Cronómetro deportivo", "Cinturón lumbar", "Colchoneta plegable", "Patines"],
        (99, 2500),
    ),
    "Belleza": (
        ["Crema hidratante facial", "Shampoo 400ml", "Acondicionador 400ml", "Set de brochas de maquillaje",
         "Perfume 50ml", "Bloqueador solar SPF50", "Set de esmaltes", "Secadora de cabello",
         "Plancha para cabello", "Kit de manicure", "Jabón artesanal", "Exfoliante corporal",
         "Mascarilla facial (set)", "Gel para cabello", "Desodorante roll-on", "Espejo con luz LED",
         "Rizador de cabello", "Loción corporal", "Removedor de maquillaje", "Cepillo para cabello"],
        (79, 1200),
    ),
    "Herramientas": (
        ["Set de destornilladores", "Taladro inalámbrico", "Martillo", "Cinta métrica 5m",
         "Set de llaves Allen", "Pinzas de electricista", "Nivel de burbuja", "Caja de herramientas",
         "Multímetro digital", "Sierra manual", "Cautín para soldar", "Guantes de trabajo",
         "Lentes de seguridad", "Cinta aislante", "Extensión para taladro", "Prensa de banco pequeña",
         "Lija (paquete surtido)", "Escalera plegable", "Candado de seguridad", "Linterna recargable"],
        (99, 3200),
    ),
    "Mascotas": (
        ["Alimento para perro 3kg", "Alimento para gato 3kg", "Correa retráctil", "Cama para mascota",
         "Arenero para gato", "Juguete mordedor", "Transportadora pequeña", "Shampoo para mascotas",
         "Comedero doble", "Rascador para gato", "Collar antipulgas", "Snacks para perro (bolsa)",
         "Bebedero automático", "Cepillo para pelo", "Ropa para perro pequeño", "Pelota interactiva",
         "Tapete absorbente", "Jaula para roedor", "Acuario pequeño", "Correa de entrenamiento"],
        (59, 1800),
    ),
}


def sembrar_productos():
    total_activos = Producto.query.filter_by(activo=True).count()
    if total_activos >= MINIMO_PRODUCTOS:
        return

    random.seed(42)  # reproducible: mismos datos en cada entorno/miembro del equipo
    categoria_repo = CategoriaRepositorio()
    creados = 0

    for nombre_categoria, (nombres, (precio_min, precio_max)) in CATALOGO.items():
        categoria = categoria_repo.obtener_o_crear(nombre_categoria)
        for nombre_base in nombres:
            if Producto.query.filter_by(nombre=nombre_base, categoria_id=categoria.id).first():
                continue
            precio = round(random.uniform(precio_min, precio_max), 2)
            stock = random.choice([0, 3, 4] + list(range(6, 80)))  # algunos en 0 o bajo stock_minimo a propósito
            producto = Producto(
                nombre=nombre_base,
                descripcion=f"{nombre_base} - categoría {nombre_categoria}",
                precio=precio,
                cantidad_stock=stock,
                stock_minimo=5,
                categoria_id=categoria.id,
                activo=True,
            )
            db.session.add(producto)
            creados += 1

    db.session.commit()
    print(f">> Seed de catálogo: {creados} productos creados "
          f"(total activos ahora: {Producto.query.filter_by(activo=True).count()})")
