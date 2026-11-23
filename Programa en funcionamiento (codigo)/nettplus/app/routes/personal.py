"""M2 Gestión de colaboradores (RF-02-3, RF-02-4)."""
from flask import Blueprint, render_template, request

from app.db import get_db
from app.repositories import colaborador_repo
from app.seguridad import ASISTENTE, DESARROLLO, JEFE, login_requerido

bp = Blueprint("personal", __name__, url_prefix="/personal")


@bp.route("/")
@login_requerido(roles=(ASISTENTE, JEFE, DESARROLLO))
def lista():
    db = get_db()
    texto = request.args.get("q", "").strip()
    depto = request.args.get("departamento", type=int)
    return render_template("personal/lista.html", colaboradores=colaborador_repo.listar(db, texto, depto),
                           departamentos=colaborador_repo.departamentos(db), q=texto, depto=depto)
