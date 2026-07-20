import os
from dotenv import load_dotenv

# load_dotenv no sobreescribe variables ya definidas en el entorno
# (así, en Docker, las variables del docker-compose.yml tienen prioridad)
load_dotenv()


class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "altrix_db")
    DB_USER = os.getenv("DB_USER", "altrix_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "altrix_pass")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
