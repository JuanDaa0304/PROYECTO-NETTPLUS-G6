"""M2 Historial de asistencia (RF-02-5, RF-02-6, RF-02-7)."""
from flask import Blueprint, current_app, render_template, request

from app.db import get_db
from app.repositories import asistencia_repo, colaborador_repo
from app.seguridad import ASISTENTE, DESARROLLO, JEFE, login_requerido
from app.services.periodo import a_fecha, periodo_de, ultimos_periodos

bp = Blueprint("marcaciones", __name__, url_prefix="/marcaciones")


@bp.route("/")
@login_requerido(roles=(ASISTENTE, JEFE, DESARROLLO))
def historial():
    db = get_db()
    args = request.args
    desde, hasta = args.get("desde", ""), args.get("hasta", "")
    periodo = args.get("periodo", "")
    if periodo:  # RN-04: periodo de corte 21–20
        inicio = a_fecha(periodo)
        if inicio:
            ini, fin = periodo_de(inicio)
            desde, hasta = ini.isoformat(), fin.isoformat()
    error = None
    if desde and hasta and desde > hasta:  # RN-05
        error = "La fecha inicial no puede ser mayor que la final."
        desde = hasta = ""
    texto = args.get("q", "").strip()
    depto = args.get("departamento", type=int)
    pagina = max(args.get("pagina", 1, type=int), 1)
    por_pagina = current_app.config["POR_PAGINA"]
    filas, total = asistencia_repo.historial(db, desde or None, hasta or None, depto, texto,
                                             por_pagina, (pagina - 1) * por_pagina)
    colaborador = colaborador_repo.obtener(db, texto) if texto else None
    return render_template(
        "marcaciones/historial.html", filas=filas, total=total, pagina=pagina,
        paginas=max((total + por_pagina - 1) // por_pagina, 1), desde=desde, hasta=hasta, q=texto,
        depto=depto, periodo=periodo, periodos=ultimos_periodos(), error=error,
        departamentos=colaborador_repo.departamentos(db), colaborador=colaborador,
    )
