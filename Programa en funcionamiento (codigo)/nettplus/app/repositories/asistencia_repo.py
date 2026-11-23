"""Acceso a datos de registros de asistencia (marcaciones)."""


def existe(db, id_colaborador, fecha, hora):
    return db.execute(
        "SELECT 1 FROM registros_asistencia WHERE id_colaborador = ? AND fecha = ? AND hora_marcacion = ?",
        (id_colaborador, fecha, hora),
    ).fetchone() is not None


def insertar_lote(db, id_importacion, registros):
    db.executemany(
        "INSERT INTO registros_asistencia (id_colaborador, fecha, hora_marcacion, tipo_marcacion, forma_marcacion, fuente, id_importacion) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        [(r["id"], r["fecha"], r["hora"], r["tipo"], r["forma"], r["fuente"], id_importacion) for r in registros],
    )


def tipos_del_dia(db, id_colaborador, fecha):
    filas = db.execute(
        "SELECT tipo_marcacion FROM registros_asistencia WHERE id_colaborador = ? AND fecha = ? ORDER BY hora_marcacion",
        (id_colaborador, fecha),
    ).fetchall()
    return [f[0] for f in filas]


def _filtros(desde, hasta, id_departamento, texto):
    sql, params = "", []
    if desde:
        sql += " AND r.fecha >= ?"; params.append(desde)
    if hasta:
        sql += " AND r.fecha <= ?"; params.append(hasta)
    if id_departamento:
        sql += " AND c.id_departamento = ?"; params.append(id_departamento)
    if texto:
        sql += " AND (c.id_colaborador = ? OR c.nombres LIKE ?)"; params += [texto, f"%{texto}%"]
    return sql, params


def historial(db, desde=None, hasta=None, id_departamento=None, texto="", limite=25, desplazamiento=0):
    filtro, params = _filtros(desde, hasta, id_departamento, texto)
    base = ("FROM registros_asistencia r JOIN colaboradores c ON c.id_colaborador = r.id_colaborador "
            "LEFT JOIN departamentos d ON d.id_departamento = c.id_departamento WHERE 1 = 1" + filtro)
    total = db.execute("SELECT COUNT(*) " + base, params).fetchone()[0]
    filas = db.execute(
        "SELECT r.*, c.nombres, d.nombre AS departamento " + base +
        " ORDER BY r.fecha DESC, c.nombres, r.hora_marcacion LIMIT ? OFFSET ?",
        params + [limite, desplazamiento],
    ).fetchall()
    return filas, total


def marcaciones_del_dia(db, fecha, id_departamento=None):
    sql = ("SELECT c.id_colaborador, c.nombres, d.nombre AS departamento, "
           "  MIN(CASE WHEN r.tipo_marcacion = 'Entrada' THEN r.hora_marcacion END) AS primera_entrada, "
           "  MAX(CASE WHEN r.tipo_marcacion = 'Salida' THEN r.hora_marcacion END) AS ultima_salida, "
           "  COUNT(r.id_registro) AS marcaciones "
           "FROM colaboradores c LEFT JOIN departamentos d ON d.id_departamento = c.id_departamento "
           "LEFT JOIN registros_asistencia r ON r.id_colaborador = c.id_colaborador AND r.fecha = ? "
           "WHERE c.estado_laboral = 'ACTIVO'")
    params = [fecha]
    if id_departamento:
        sql += " AND c.id_departamento = ?"
        params.append(id_departamento)
    sql += " GROUP BY c.id_colaborador ORDER BY d.nombre, c.nombres"
    return db.execute(sql, params).fetchall()


def ultima_fecha(db):
    return db.execute("SELECT MAX(fecha) FROM registros_asistencia").fetchone()[0]


def contar(db):
    return db.execute("SELECT COUNT(*) FROM registros_asistencia").fetchone()[0]


def por_dia(db, dias=10):
    return db.execute(
        "SELECT fecha, COUNT(*) AS total, COUNT(DISTINCT id_colaborador) AS personas FROM registros_asistencia "
        "GROUP BY fecha ORDER BY fecha DESC LIMIT ?",
        (dias,),
    ).fetchall()[::-1]
