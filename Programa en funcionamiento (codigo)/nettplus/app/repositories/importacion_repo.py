"""Acceso a datos de importaciones e incidencias."""


def crear(db, id_usuario, nombre_archivo, formato):
    cur = db.execute(
        "INSERT INTO importaciones (id_usuario, nombre_archivo, formato_archivo, resultado) VALUES (?, ?, ?, 'EN PROCESO')",
        (id_usuario, nombre_archivo, formato),
    )
    return cur.lastrowid


def guardar_incidencias(db, id_importacion, incidencias):
    db.executemany(
        "INSERT INTO incidencias_importacion (id_importacion, numero_fila, tipo_incidencia, descripcion) VALUES (?, ?, ?, ?)",
        [(id_importacion, fila, tipo, desc) for fila, tipo, desc in incidencias],
    )


def cerrar(db, id_importacion, leidos, cargados, errores, resultado):
    db.execute(
        "UPDATE importaciones SET registros_leidos = ?, registros_cargados = ?, registros_con_error = ?, resultado = ? "
        "WHERE id_importacion = ?",
        (leidos, cargados, errores, resultado, id_importacion),
    )


def listar(db, limite=50):
    return db.execute(
        "SELECT i.*, u.nombre AS usuario, "
        "  (SELECT COUNT(*) FROM incidencias_importacion x WHERE x.id_importacion = i.id_importacion) AS incidencias "
        "FROM importaciones i LEFT JOIN usuarios u ON u.id_usuario = i.id_usuario "
        "ORDER BY i.id_importacion DESC LIMIT ?",
        (limite,),
    ).fetchall()


def obtener(db, id_importacion):
    return db.execute(
        "SELECT i.*, u.nombre AS usuario FROM importaciones i LEFT JOIN usuarios u ON u.id_usuario = i.id_usuario "
        "WHERE i.id_importacion = ?",
        (id_importacion,),
    ).fetchone()


def incidencias(db, id_importacion):
    return db.execute(
        "SELECT * FROM incidencias_importacion WHERE id_importacion = ? ORDER BY tipo_incidencia, numero_fila",
        (id_importacion,),
    ).fetchall()


def ultima(db):
    return db.execute("SELECT * FROM importaciones ORDER BY id_importacion DESC LIMIT 1").fetchone()


def total_incidencias(db):
    return db.execute("SELECT COUNT(*) FROM incidencias_importacion").fetchone()[0]
