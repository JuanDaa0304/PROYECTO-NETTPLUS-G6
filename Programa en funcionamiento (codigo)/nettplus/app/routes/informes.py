"""M4 Informes: parte diario de asistencia (RF-04-1)."""
from datetime import date

from flask import Blueprint, render_template, request

from app.db import get_db
from app.repositories import asistencia_repo, colaborador_repo
from app.seguridad import ASISTENTE, JEFE, login_requerido
from app.services import asistencia_service

bp = Blueprint("informes", __name__, url_prefix="/informes")


@bp.route("/parte-diario")
@login_requerido(roles=(ASISTENTE, JEFE))
def parte_diario():
    db = get_db()
    fecha = request.args.get("fecha") or asistencia_repo.ultima_fecha(db) or date.today().isoformat()
    depto = request.args.get("departamento", type=int)
    detalle, resumen = asistencia_service.parte_diario(db, fecha, depto)
    return render_template("informes/parte_diario.html", fecha=fecha, detalle=detalle, resumen=resumen,
                           departamentos=colaborador_repo.departamentos(db), depto=depto)
