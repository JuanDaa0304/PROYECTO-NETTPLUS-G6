"""Configuración general de la aplicación NettPlus."""
import os
import secrets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    # Clave de sesión: se toma de la variable de entorno; si no existe se genera una.
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))

    # Base de datos SQLite dentro de la carpeta data/
    DATABASE = os.environ.get("NETTPLUS_DB", os.path.join(BASE_DIR, "data", "nettplus.db"))

    # Límite de tamaño del archivo Excel (10 MB)
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    # RNF-16: cierre de sesión tras 15 minutos de inactividad
    MINUTOS_INACTIVIDAD = 15

    # Hora de entrada por defecto mientras no se importen los horarios (RF-01-10, Sprint 3)
    HORA_ENTRADA_DEFECTO = "08:00"
    TOLERANCIA_MINUTOS = 5

    # Registros por página en las tablas
    POR_PAGINA = 25
