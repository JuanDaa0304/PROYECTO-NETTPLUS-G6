"""M5 Seguridad: inicio y cierre de sesión (RF-05-1, RF-05-2)."""
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from app.db import get_db
from app.repositories import auditoria_repo, usuario_repo

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        db = get_db()
        nombre_usuario = request.form.get("usuario", "").strip()
        usuario = usuario_repo.por_nombre_usuario(db, nombre_usuario)
        if usuario and usuario["estado_cuenta"] == "ACTIVA" and check_password_hash(
            usuario["contrasena_hash"], request.form.get("password", "")
        ):
            session.clear()
            session.update({
                "id_usuario": usuario["id_usuario"], "usuario": usuario["nombre_usuario"],
                "nombre": usuario["nombre"], "id_rol": usuario["id_rol"], "rol": usuario["rol"],
                "ultima_actividad": datetime.now().isoformat(),
            })
            auditoria_repo.registrar(db, usuario["id_usuario"], "INICIO_SESION")
            db.commit()
            siguiente = request.args.get("siguiente", "")
            return redirect(siguiente if siguiente.startswith("/") else url_for("panel.inicio"))
        auditoria_repo.registrar(db, None, "ACCESO_RECHAZADO", f"usuario: {nombre_usuario}")
        db.commit()
        flash("Usuario o contraseña incorrectos. Inténtalo de nuevo.", "error")
    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    if "id_usuario" in session:
        db = get_db()
        auditoria_repo.registrar(db, session["id_usuario"], "CIERRE_SESION")
        db.commit()
    session.clear()
    flash("Sesión cerrada correctamente.", "exito")
    return redirect(url_for("auth.login"))
