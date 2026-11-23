"""Lógica de negocio de consultas e informes de asistencia.

RF-02-5/02-6/02-7 historial · RF-04-1 parte (resumen) diario · RN-10 atraso
"""
from datetime import date, datetime

from flask import current_app

from app.repositories import asistencia_repo, colaborador_repo, importacion_repo
from app.services.periodo import periodo_de


def _minutos(hora):
    h, m = hora.split(":")
    return int(h) * 60 + int(m)


def minutos_atraso(primera_entrada):
    """RN-10: atraso = entrada posterior a la hora de inicio + tolerancia.
    Mientras no se importen horarios (RF-01-10) se usa la hora configurada."""
    if not primera_entrada:
        return 0
    inicio = _minutos(current_app.config["HORA_ENTRADA_DEFECTO"])
    diferencia = _minutos(primera_entrada) - inicio
    return diferencia if diferencia > current_app.config["TOLERANCIA_MINUTOS"] else 0


def parte_diario(db, fecha, id_departamento=None):
    filas = asistencia_repo.marcaciones_del_dia(db, fecha, id_departamento)
    detalle, resumen = [], {"presentes": 0, "ausentes": 0, "atrasos": 0, "observados": 0}
    for f in filas:
        atraso = minutos_atraso(f["primera_entrada"])
        if f["marcaciones"] == 0:
            estado = "Sin marcación"
            resumen["ausentes"] += 1
        elif f["marcaciones"] % 2 == 1:
            estado = "Revisar"
            resumen["observados"] += 1
            resumen["presentes"] += 1
        elif atraso:
            estado = "Atraso"
            resumen["atrasos"] += 1
            resumen["presentes"] += 1
        else:
            estado = "A tiempo"
            resumen["presentes"] += 1
        detalle.append({**dict(f), "atraso": atraso, "estado": estado})
    return detalle, resumen


def indicadores_inicio(db):
    """Datos de la pantalla de inicio."""
    ultima_fecha = asistencia_repo.ultima_fecha(db)
    inicio_p, fin_p = periodo_de(date.today())
    datos = {
        "colaboradores": colaborador_repo.contar(db),
        "marcaciones": asistencia_repo.contar(db),
        "incidencias": importacion_repo.total_incidencias(db),
        "ultima_carga": importacion_repo.ultima(db),
        "ultima_fecha": ultima_fecha,
        "periodo": (inicio_p, fin_p),
        "por_dia": asistencia_repo.por_dia(db, 10),
        "resumen": None,
    }
    if ultima_fecha:
        _, datos["resumen"] = parte_diario(db, ultima_fecha)
    return datos


def formato_fecha_hora(texto):
    try:
        return datetime.strptime(texto[:16], "%Y-%m-%d %H:%M").strftime("%d/%m/%Y %H:%M")
    except (TypeError, ValueError):
        return texto or "—"


def formato_fecha(texto):
    try:
        return datetime.strptime(texto, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return texto or "—"
