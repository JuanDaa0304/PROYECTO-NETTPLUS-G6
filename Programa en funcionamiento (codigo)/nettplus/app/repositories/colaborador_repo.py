"""Acceso a datos de colaboradores y departamentos."""


def guardar_departamento(db, id_departamento, nombre):
    db.execute(
        "INSERT INTO departamentos (id_departamento, nombre) VALUES (?, ?) "
        "ON CONFLICT(id_departamento) DO UPDATE SET nombre = excluded.nombre",
        (id_departamento, nombre),
    )


def guardar(db, id_colaborador, nombres, id_departamento, id_cargo):
    db.execute(
        "INSERT INTO colaboradores (id_colaborador, nombres, id_departamento, id_cargo) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(id_colaborador) DO UPDATE SET nombres = excluded.nombres, "
        "id_departamento = COALESCE(excluded.id_departamento, colaboradores.id_departamento), "
        "id_cargo = COALESCE(excluded.id_cargo, colaboradores.id_cargo)",
        (id_colaborador, nombres, id_departamento, id_cargo),
    )


def departamentos(db):
    return db.execute("SELECT * FROM departamentos ORDER BY nombre").fetchall()


def listar(db, texto="", id_departamento=None):
    sql = ("SELECT c.*, d.nombre AS departamento, "
           "  (SELECT COUNT(*) FROM registros_asistencia r WHERE r.id_colaborador = c.id_colaborador) AS marcaciones, "
           "  (SELECT MAX(fecha) FROM registros_asistencia r WHERE r.id_colaborador = c.id_colaborador) AS ultima_fecha "
           "FROM colaboradores c LEFT JOIN departamentos d ON d.id_departamento = c.id_departamento WHERE 1 = 1")
    params = []
    if texto:
        sql += " AND (c.id_colaborador = ? OR c.nombres LIKE ?)"
        params += [texto, f"%{texto}%"]
    if id_departamento:
        sql += " AND c.id_departamento = ?"
        params.append(id_departamento)
    sql += " ORDER BY c.nombres"
    return db.execute(sql, params).fetchall()


def obtener(db, id_colaborador):
    return db.execute(
        "SELECT c.*, d.nombre AS departamento FROM colaboradores c "
        "LEFT JOIN departamentos d ON d.id_departamento = c.id_departamento WHERE c.id_colaborador = ?",
        (id_colaborador,),
    ).fetchone()


def contar(db):
    return db.execute("SELECT COUNT(*) FROM colaboradores WHERE estado_laboral = 'ACTIVO'").fetchone()[0]
