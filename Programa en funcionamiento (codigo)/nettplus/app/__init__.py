"""Fábrica de la aplicación NettPlus (Flask)."""
from flask import Flask, render_template, session

from app.config import Config
from app.db import init_db


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    init_db(app)

    from app.routes import auth, importacion, informes, marcaciones, panel, personal, sistema
    for modulo in (auth, panel, importacion, personal, marcaciones, informes, sistema):
        app.register_blueprint(modulo.bp)

    from app.seguridad import menu_para
    from app.services.asistencia_service import formato_fecha, formato_fecha_hora
    from app.services.periodo import nombre_periodo, periodo_de

    @app.context_processor
    def datos_layout():
        if "id_rol" not in session:
            return {}
        from datetime import date
        ini, fin = periodo_de(date.today())
        hoy = date.today()
        total = (fin - ini).days + 1
        dia = (hoy - ini).days + 1
        return {"menu": menu_para(session["id_rol"]), "periodo_actual": nombre_periodo(ini, fin),
                "corte_dia": dia, "corte_total": total, "corte_pct": round(dia * 100 / total)}

    app.jinja_env.filters["fecha"] = formato_fecha
    app.jinja_env.filters["fechahora"] = formato_fecha_hora

    @app.errorhandler(404)
    def no_encontrado(_e):
        return render_template("errores/error.html", codigo=404, mensaje="La página que buscas no existe."), 404

    @app.errorhandler(413)
    def archivo_grande(_e):
        return render_template("errores/error.html", codigo=413, mensaje="El archivo supera el límite de 10 MB."), 413

    return app
