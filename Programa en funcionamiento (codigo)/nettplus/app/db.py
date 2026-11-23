"""Capa de acceso a datos: conexión SQLite y creación del esquema.

El esquema sigue el diagrama de clases de Enterprise Architect (paquete 05).
"""
import os
import sqlite3

from flask import current_app, g
from werkzeug.security import generate_password_hash

ESQUEMA = """
CREATE TABLE IF NOT EXISTS roles (
    id_rol      INTEGER PRIMARY KEY,
    nombre      TEXT UNIQUE NOT NULL,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_usuario  TEXT UNIQUE NOT NULL,
    nombre          TEXT NOT NULL,
    contrasena_hash TEXT NOT NULL,
    id_rol          INTEGER NOT NULL REFERENCES roles(id_rol),
    estado_cuenta   TEXT NOT NULL DEFAULT 'ACTIVA'
);

CREATE TABLE IF NOT EXISTS departamentos (
    id_departamento INTEGER PRIMARY KEY,
    nombre          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS colaboradores (
    id_colaborador  TEXT PRIMARY KEY,
    nombres         TEXT NOT NULL,
    id_departamento INTEGER REFERENCES departamentos(id_departamento),
    id_cargo        TEXT,
    estado_laboral  TEXT NOT NULL DEFAULT 'ACTIVO'
);

CREATE TABLE IF NOT EXISTS importaciones (
    id_importacion      INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora          TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    id_usuario          INTEGER REFERENCES usuarios(id_usuario),
    nombre_archivo      TEXT NOT NULL,
    tipo_importacion    TEXT NOT NULL DEFAULT 'MARCACIONES',
    formato_archivo     TEXT,
    registros_leidos    INTEGER NOT NULL DEFAULT 0,
    registros_cargados  INTEGER NOT NULL DEFAULT 0,
    registros_con_error INTEGER NOT NULL DEFAULT 0,
    resultado           TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS registros_asistencia (
    id_registro      INTEGER PRIMARY KEY AUTOINCREMENT,
    id_colaborador   TEXT NOT NULL REFERENCES colaboradores(id_colaborador),
    fecha            TEXT NOT NULL,
    hora_marcacion   TEXT NOT NULL,
    tipo_marcacion   TEXT NOT NULL,
    forma_marcacion  TEXT,
    fuente           TEXT,
    id_importacion   INTEGER NOT NULL REFERENCES importaciones(id_importacion),
    UNIQUE (id_colaborador, fecha, hora_marcacion)
);

CREATE TABLE IF NOT EXISTS incidencias_importacion (
    id_incidencia   INTEGER PRIMARY KEY AUTOINCREMENT,
    id_importacion  INTEGER NOT NULL REFERENCES importaciones(id_importacion) ON DELETE CASCADE,
    numero_fila     INTEGER,
    tipo_incidencia TEXT NOT NULL,
    descripcion     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eventos_auditoria (
    id_evento  INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    id_usuario INTEGER REFERENCES usuarios(id_usuario),
    accion     TEXT NOT NULL,
    detalle    TEXT
);

CREATE INDEX IF NOT EXISTS ix_registro_fecha ON registros_asistencia(fecha);
CREATE INDEX IF NOT EXISTS ix_registro_colab ON registros_asistencia(id_colaborador);
"""

ROLES = [
    (1, "Asistente de RR.HH.", "Importa archivos, consulta y genera reportes"),
    (2, "Jefe de área", "Consulta la asistencia de su área"),
    (3, "Contabilidad", "Consulta reportes mensuales para nómina"),
    (4, "Desarrollo organizacional", "Indicadores, trazabilidad y administración de cuentas"),
]

# Usuarios de prueba (cambiar las contraseñas antes de usar en producción)
USUARIOS_DEMO = [
    ("admin", "Administrador RR.HH.", "admin123", 1),
    ("desarrollo", "Desarrollo Organizacional", "desarrollo123", 4),
    ("jefe", "Jefe de Logística", "jefe123", 2),
    ("contabilidad", "Contabilidad", "conta123", 3),
]


def get_db():
    """Devuelve la conexión de la petición actual (una por petición)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Crea la carpeta data/, las tablas y los datos iniciales."""
    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)
    with sqlite3.connect(app.config["DATABASE"]) as conn:
        conn.executescript(ESQUEMA)
        conn.executemany("INSERT OR IGNORE INTO roles VALUES (?, ?, ?)", ROLES)
        for usuario, nombre, clave, rol in USUARIOS_DEMO:
            existe = conn.execute(
                "SELECT 1 FROM usuarios WHERE nombre_usuario = ?", (usuario,)
            ).fetchone()
            if not existe:
                conn.execute(
                    "INSERT INTO usuarios (nombre_usuario, nombre, contrasena_hash, id_rol) VALUES (?, ?, ?, ?)",
                    (usuario, nombre, generate_password_hash(clave), rol),
                )
    app.teardown_appcontext(close_db)
