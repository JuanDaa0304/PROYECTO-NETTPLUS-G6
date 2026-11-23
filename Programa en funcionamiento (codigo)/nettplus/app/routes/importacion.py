"""M1 Importación de datos (RF-01-1 a RF-01-8)."""
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from app.db import get_db
from app.repositories import importacion_repo
from app.seguridad import ASISTENTE, DESARROLLO, login_requerido
from app.services import importacion_service

bp = Blueprint("importacion", __name__, url_prefix="/cargas")


@bp.route("/nueva", methods=["GET", "POST"])
@login_requerido(roles=(ASISTENTE,))
def cargar():
    if request.method == "POST":
        resultado = importacion_service.procesar_archivo(get_db(), request.files.get("archivo"), session["id_usuario"])
        if "id_importacion" not in resultado:
            flash(resultado["mensaje"], "error")
            return redirect(url_for("importacion.cargar"))
        flash(resultado["mensaje"], "exito" if resultado["ok"] else "error")
        return redirect(url_for("importacion.detalle", id_importacion=resultado["id_importacion"]))
    return render_template("importacion/cargar.html", recientes=importacion_repo.listar(get_db(), 5))


@bp.route("/")
@login_requerido(roles=(ASISTENTE, DESARROLLO))
def registro():
    return render_template("importacion/registro.html", cargas=importacion_repo.listar(get_db()))


@bp.route("/<int:id_importacion>")
@login_requerido(roles=(ASISTENTE, DESARROLLO))
def detalle(id_importacion):
    db = get_db()
    carga = importacion_repo.obtener(db, id_importacion)
    if carga is None:
        abort(404)
    return render_template("importacion/detalle.html", c=carga, incidencias=importacion_repo.incidencias(db, id_importacion))
