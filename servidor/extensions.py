from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient

db = SQLAlchemy()

# Variables globales para MongoDB
mongo_client = None
mongo_db = None

def init_mongo(app):
    global mongo_client, mongo_db
    if app.config['MONGO_URI']:
        mongo_client = MongoClient(app.config['MONGO_URI'])
        # Obtiene la base de datos definida en la URI (por defecto 'altrix')
        mongo_db = mongo_client.get_default_database()