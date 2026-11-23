"""Acceso a datos de eventos de auditoría (RF-05-6)."""


def registrar(db, id_usuario, accion, detalle=""):
    db.execute(
        "INSERT INTO eventos_auditoria (id_usuario, accion, detalle) VALUES (?, ?, ?)",
        (id_usuario, accion, detalle),
    )
