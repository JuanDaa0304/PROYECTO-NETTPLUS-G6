"""Pruebas unitarias (RNF-18). Ejecutar con:  python -m pytest"""
import os
from datetime import date

from conftest import EJEMPLOS, ingresar
from app.services.periodo import periodo_de


def subir(cliente, nombre):
    with open(os.path.join(EJEMPLOS, nombre), "rb") as f:
        return cliente.post("/cargas/nueva", data={"archivo": (f, nombre)},
                            content_type="multipart/form-data", follow_redirects=True)


def test_periodo_de_corte_21_al_20():
    assert periodo_de(date(2026, 11, 23)) == (date(2026, 11, 21), date(2026, 12, 20))
    assert periodo_de(date(2026, 11, 20)) == (date(2026, 10, 21), date(2026, 11, 20))
    assert periodo_de(date(2026, 1, 5)) == (date(2025, 12, 21), date(2026, 1, 20))


def test_login_correcto_e_incorrecto(cliente):
    assert "Usuario o contraseña incorrectos" in ingresar(cliente, "admin", "mala").get_data(as_text=True)
    assert "Hola" in ingresar(cliente).get_data(as_text=True)


def test_pagina_protegida_sin_sesion(cliente):
    respuesta = cliente.get("/marcaciones/")
    assert respuesta.status_code == 302 and "/login" in respuesta.headers["Location"]


def test_menu_segun_rol(cliente):
    html = ingresar(cliente, "contabilidad", "conta123").get_data(as_text=True)
    assert "Cierre de periodo" in html and "Carga de marcaciones" not in html
    assert cliente.get("/cargas/nueva", follow_redirects=True).get_data(as_text=True).count("no tiene permiso") == 1


def test_carga_detecta_duplicados_e_incompletos(cliente):
    ingresar(cliente)
    html = subir(cliente, "marcaciones_demo_hoja_unica.xlsx").get_data(as_text=True)
    assert "Duplicado" in html and "Incompleto" in html and "Con observaciones" in html
    # volver a subir el mismo archivo: todo duplicado, no se guarda nada nuevo
    html = subir(cliente, "marcaciones_demo_hoja_unica.xlsx").get_data(as_text=True)
    assert "Fallida" in html


def test_formato_una_hoja_por_colaborador(cliente):
    ingresar(cliente)
    html = subir(cliente, "marcaciones_demo_por_colaborador.xlsx").get_data(as_text=True)
    assert "una hoja por colaborador" in html


def test_archivo_no_excel(cliente):
    ingresar(cliente)
    from io import BytesIO
    html = cliente.post("/cargas/nueva", data={"archivo": (BytesIO(b"hola"), "datos.csv")},
                        content_type="multipart/form-data", follow_redirects=True).get_data(as_text=True)
    assert "Formato no compatible" in html


def test_consultas_y_parte_diario(cliente):
    ingresar(cliente)
    subir(cliente, "Reporte de Marcaciones_ejemplo_NetPlus.xlsx")
    assert "Prueba 1" in cliente.get("/personal/").get_data(as_text=True)
    assert "Prueba 1" in cliente.get("/marcaciones/?q=4").get_data(as_text=True)
    html = cliente.get("/informes/parte-diario?fecha=2026-10-17").get_data(as_text=True)
    assert "Atraso" in html  # entró 08:24
