"""Reglas de fechas de NetPlus.

RN-04: el periodo de corte va del día 21 de un mes al día 20 del mes siguiente.
"""
from datetime import date, datetime

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def periodo_de(fecha):
    """Devuelve (inicio, fin) del periodo de corte que contiene la fecha."""
    if fecha.day >= 21:
        inicio = date(fecha.year, fecha.month, 21)
        fin_mes, fin_anio = (fecha.month % 12) + 1, fecha.year + (1 if fecha.month == 12 else 0)
        fin = date(fin_anio, fin_mes, 20)
    else:
        ini_mes = 12 if fecha.month == 1 else fecha.month - 1
        ini_anio = fecha.year - 1 if fecha.month == 1 else fecha.year
        inicio = date(ini_anio, ini_mes, 21)
        fin = date(fecha.year, fecha.month, 20)
    return inicio, fin


def nombre_periodo(inicio, fin):
    return f"{inicio.day} {MESES[inicio.month - 1][:3]} – {fin.day} {MESES[fin.month - 1][:3]} {fin.year}"


def ultimos_periodos(cantidad=6, referencia=None):
    """Lista de los últimos periodos de corte: [(clave, texto, inicio, fin)]."""
    ref = referencia or date.today()
    salida = []
    inicio, fin = periodo_de(ref)
    for _ in range(cantidad):
        salida.append((inicio.isoformat(), nombre_periodo(inicio, fin), inicio, fin))
        inicio, fin = periodo_de(date.fromordinal(inicio.toordinal() - 1))
    return salida


def a_fecha(texto):
    """Convierte 'YYYY-MM-DD' en date; devuelve None si no es válido."""
    try:
        return datetime.strptime(texto, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None
