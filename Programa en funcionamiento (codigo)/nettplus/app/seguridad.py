"""Seguridad: sesión, inactividad (RNF-16) y permisos por rol (RF-05-3).

El MENU define las opciones de la barra lateral y qué roles pueden verlas.
Roles: 1 Asistente de RR.HH. · 2 Jefe de área · 3 Contabilidad · 4 Desarrollo organizacional
"""
from datetime import datetime, timedelta
from functools import wraps

from flask import current_app, flash, redirect, request, session, url_for

ASISTENTE, JEFE, CONTABILIDAD, DESARROLLO = 1, 2, 3, 4
TODOS = (ASISTENTE, JEFE, CONTABILIDAD, DESARROLLO)

# (sección, [(endpoint, texto, icono, roles, sprint_pendiente)])
MENU = [
    ("Operación", [
        ("panel.inicio", "Inicio", "inicio", TODOS, None),
        ("importacion.cargar", "Carga de marcaciones", "carga", (ASISTENTE,), None),
        ("importacion.registro", "Registro de cargas", "registro", (ASISTENTE, DESARROLLO), None),
    ]),
    ("Consultas", [
        ("personal.lista", "Personal", "personal", (ASISTENTE, JEFE, DESARROLLO), None),
        ("marcaciones.historial", "Marcaciones", "marcaciones", (ASISTENTE, JEFE, DESARROLLO), None),
    ]),
    ("Informes", [
        ("informes.parte_diario", "Parte diario", "parte", (ASISTENTE, JEFE), None),
        ("sistema.proximamente:indicadores", "Indicadores", "indicadores", (ASISTENTE, JEFE, DESARROLLO), "Sprint 3"),
        ("sistema.proximamente:cierre", "Cierre de periodo", "cierre", (ASISTENTE, CONTABILIDAD, DESARROLLO), "Sprint 3"),
    ]),
    ("Sistema", [
        ("sistema.proximamente:cuentas", "Cuentas y roles", "cuentas", (DESARROLLO,), "Sprint 3"),
        ("sistema.proximamente:trazabilidad", "Trazabilidad", "trazabilidad", (ASISTENTE, DESARROLLO), "Sprint 3"),
    ]),
]


def menu_para(id_rol):
    """Devuelve solo las opciones del menú permitidas para el rol."""
    salida = []
    for seccion, items in MENU:
        visibles = []
        for endpoint, texto, icono, roles, sprint in items:
            if id_rol in roles:
                if ":" in endpoint:
                    ep, modulo = endpoint.split(":")
                    url = url_for(ep, modulo=modulo)
                else:
                    ep, url = endpoint, url_for(endpoint)
                visibles.append({"endpoint": ep, "url": url, "texto": texto, "icono": icono, "sprint": sprint})
        if visibles:
            salida.append((seccion, visibles))
    return salida


def login_requerido(roles=TODOS):
    """Decorador: exige sesión activa y que el rol esté permitido."""
    def decorador(vista):
        @wraps(vista)
        def envoltura(*args, **kwargs):
            if "id_usuario" not in session:
                return redirect(url_for("auth.login", siguiente=request.path))
            # RNF-16: cierre por inactividad
            ultima = session.get("ultima_actividad")
            limite = timedelta(minutes=current_app.config["MINUTOS_INACTIVIDAD"])
            if ultima and datetime.now() - datetime.fromisoformat(ultima) > limite:
                session.clear()
                flash("Tu sesión se cerró por inactividad. Ingresa de nuevo.", "aviso")
                return redirect(url_for("auth.login"))
            session["ultima_actividad"] = datetime.now().isoformat()
            if session.get("id_rol") not in roles:
                flash("Tu rol no tiene permiso para esa opción.", "error")
                return redirect(url_for("panel.inicio"))
            return vista(*args, **kwargs)
        return envoltura
    return decorador
