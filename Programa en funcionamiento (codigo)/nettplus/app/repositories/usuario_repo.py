"""Acceso a datos de usuarios y roles."""


def por_nombre_usuario(db, nombre_usuario):
    return db.execute(
        "SELECT u.*, r.nombre AS rol FROM usuarios u JOIN roles r ON r.id_rol = u.id_rol WHERE u.nombre_usuario = ?",
        (nombre_usuario,),
    ).fetchone()
