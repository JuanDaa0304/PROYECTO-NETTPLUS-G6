"""Genera archivos de prueba con el mismo formato del «Reporte de Marcaciones» de Z-BioTime.

Uso:  python data/ejemplos/generar_demo.py
Crea: marcaciones_demo_hoja_unica.xlsx y marcaciones_demo_por_colaborador.xlsx (datos ficticios).
"""
import os
import random
from datetime import date, timedelta

from openpyxl import Workbook

random.seed(7)
CARPETA = os.path.dirname(os.path.abspath(__file__))
COLUMNAS = ["Id del Empleado", "Nombres", "ID de Departamento", "Departamento", "ID del Cargo",
            "Fecha", "Hora", "Tipo de Marcación", "Tipo", "Fuente de Datos"]
PERSONAS = [
    (11, "LUCIA ARMIJOS", 7, "LOGISTICA", 19), (12, "MARIO JARAMILLO", 7, "LOGISTICA", 19),
    (13, "PAOLA RIOFRIO", 7, "LOGISTICA", 20), (21, "DIEGO ORDOÑEZ", 3, "SOPORTE TECNICO", 8),
    (22, "KARINA CUENCA", 3, "SOPORTE TECNICO", 8), (23, "JOSE SARANGO", 3, "SOPORTE TECNICO", 9),
    (24, "ANDRES VALAREZO", 3, "SOPORTE TECNICO", 9), (31, "VALERIA LEON", 5, "VENTAS", 12),
    (32, "FERNANDO CARRION", 5, "VENTAS", 12), (33, "GABRIELA OJEDA", 5, "VENTAS", 13),
    (41, "RICARDO GUAMAN", 2, "ADMINISTRACION", 4), (42, "SOFIA MALDONADO", 2, "ADMINISTRACION", 5),
]


def hora(h, m, variacion):
    total = h * 60 + m + random.randint(-variacion, variacion)
    return f"{total // 60:02d}:{total % 60:02d}"


def filas():
    dia, fin = date(2026, 10, 21), date(2026, 11, 20)
    salida = []
    while dia <= fin:
        if dia.weekday() < 5:
            for pid, nom, idd, dep, car in PERSONAS:
                if random.random() < 0.06:
                    continue  # no marcó ese día
                tarde = random.random() < 0.15
                ent = hora(8, 25 if tarde else 0, 10 if tarde else 4)
                marcas = [(ent, "Entrada"), (hora(12, 2, 3), "Salida"), (hora(14, 58, 4), "Entrada"), (hora(19, 0, 4), "Salida")]
                if random.random() < 0.03:
                    marcas = marcas[:3]  # olvidó marcar la salida
                for h, t in marcas:
                    movil = t == "Salida" and random.random() < 0.2
                    salida.append([str(pid), nom, str(idd), dep, str(car), dia.strftime("%d-%m-%Y"), h, t,
                                   "Cualquiera" if movil else "Rostro&Huella", "Mobil" if movil else "Dispositivo"])
        dia += timedelta(days=1)
    # errores intencionales para probar la validación
    salida.append(list(salida[5]))                         # duplicado
    salida.append(["21", "DIEGO ORDOÑEZ", "3", "SOPORTE TECNICO", "8", "", "08:00", "Entrada", "Rostro&Huella", "Dispositivo"])  # sin fecha
    return salida


def hoja(ws, datos):
    ws.append(["Reporte de Marcaciones"])
    ws.append(COLUMNAS)
    for f in datos:
        ws.append(f)


def main():
    datos = filas()
    wb = Workbook(); ws = wb.active; ws.title = "20261121"; hoja(ws, datos)
    wb.save(os.path.join(CARPETA, "marcaciones_demo_hoja_unica.xlsx"))

    wb = Workbook(); wb.remove(wb.active)
    for pid, *_ in PERSONAS[:4]:
        hoja(wb.create_sheet(str(pid)), [f for f in datos if f[0] == str(pid)])
    wb.save(os.path.join(CARPETA, "marcaciones_demo_por_colaborador.xlsx"))
    print("Archivos de prueba creados en", CARPETA)


if __name__ == "__main__":
    main()
