"""Pantalla de inicio con el resumen general."""
from flask import Blueprint, render_template

from app.db import get_db
from app.seguridad import login_requerido
from app.services import asistencia_service

bp = Blueprint("panel", __name__)


@bp.route("/")
@login_requerido()
def inicio():
    datos = asistencia_service.indicadores_inicio(get_db())
    return render_template("panel/inicio.html", d=datos)
