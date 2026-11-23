"""Opciones planificadas para el Sprint 3."""
from flask import Blueprint, abort, render_template

from app.seguridad import login_requerido

bp = Blueprint("sistema", __name__)

PROXIMAMENTE = {
    "indicadores": ("Indicadores", "Dashboard de asistencia, puntualidad, horas extras y headcount por área.", "RF-03-1 a RF-03-6"),
    "cierre": ("Cierre de periodo", "Consolidado mensual por colaborador (corte 21–20) y novedades pendientes para Contabilidad.", "RF-04-2 a RF-04-7"),
    "cuentas": ("Cuentas y roles", "Crear, desactivar y asignar rol a las cuentas de usuario.", "RF-05-4"),
    "trazabilidad": ("Trazabilidad", "Historial de importaciones, correcciones y accesos.", "RF-05-5 a RF-05-7"),
}


@bp.route("/modulo/<modulo>")
@login_requerido()
def proximamente(modulo):
    if modulo not in PROXIMAMENTE:
        abort(404)
    titulo, descripcion, requisitos = PROXIMAMENTE[modulo]
    return render_template("errores/proximamente.html", titulo=titulo, descripcion=descripcion, requisitos=requisitos)
