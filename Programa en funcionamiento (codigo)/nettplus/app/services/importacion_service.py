"""Lógica de negocio del módulo M1 Importación de datos.

Cubre: RF-01-1 cargar archivo · RF-01-2 identificar formato · RF-01-3 validar campos
RF-01-4 duplicados · RF-01-5 incompletos · RF-01-6 inconsistencias
RF-01-7 almacenar registros válidos · RF-01-8 registrar resultado · RF-02-1/02-2 colaboradores
"""
import os
import re
import unicodedata
from datetime import datetime

import pandas as pd


def _dma(fecha_iso):
    return f"{fecha_iso[8:10]}/{fecha_iso[5:7]}/{fecha_iso[:4]}"

from app.repositories import asistencia_repo, auditoria_repo, colaborador_repo, importacion_repo

EXTENSIONES = {".xlsx", ".xls"}

# Columnas del "Reporte de Marcaciones" de Z-BioTime (nombre normalizado -> campo interno)
COLUMNAS = {
    "id del empleado": "id", "id empleado": "id", "codigo": "id",
    "nombres": "nombres", "nombre": "nombres",
    "id de departamento": "id_depto",
    "departamento": "depto",
    "id del cargo": "id_cargo",
    "fecha": "fecha",
    "hora": "hora",
    "tipo de marcacion": "tipo_marcacion",
    "tipo": "forma",
    "fuente de datos": "fuente",
}
OBLIGATORIOS = {"id": "Id del Empleado", "fecha": "Fecha", "hora": "Hora", "tipo_marcacion": "Tipo de Marcación"}


def _norm(texto):
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", texto).strip().lower()


def _vacio(valor):
    return valor is None or (isinstance(valor, float) and pd.isna(valor)) or str(valor).strip() in ("", "nan", "NaT")


def _fecha(valor):
    texto = str(valor).strip()
    for formato in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(texto, formato).date().isoformat()
        except ValueError:
            pass
    return None


def _hora(valor):
    texto = str(valor).strip()
    for formato in ("%H:%M", "%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(texto, formato).strftime("%H:%M")
        except ValueError:
            pass
    return None


def _id_texto(valor):
    texto = str(valor).strip()
    return texto[:-2] if texto.endswith(".0") else texto


def leer_hojas(archivo):
    """RF-01-2: lee todas las hojas y ubica la fila de encabezados de cada una."""
    hojas = pd.read_excel(archivo, sheet_name=None, header=None, dtype=str)
    encontradas = []
    for nombre_hoja, df in hojas.items():
        for i in range(min(len(df), 15)):
            fila = [_norm(v) for v in df.iloc[i].tolist()]
            if "fecha" in fila and any(c in fila for c in ("id del empleado", "id empleado", "codigo")):
                mapa = {}
                for j, celda in enumerate(fila):
                    if celda in COLUMNAS and COLUMNAS[celda] not in mapa:
                        mapa[COLUMNAS[celda]] = j
                encontradas.append((nombre_hoja, df, i, mapa))
                break
    return encontradas


def procesar_archivo(db, archivo, id_usuario):
    """Procesa el Excel de marcaciones. Devuelve un diccionario con el resultado."""
    if archivo is None or archivo.filename == "":
        return {"ok": False, "mensaje": "Debes seleccionar un archivo."}
    _, extension = os.path.splitext(archivo.filename)
    if extension.lower() not in EXTENSIONES:
        return {"ok": False, "mensaje": "Formato no compatible. Solo se admiten archivos .xlsx y .xls."}

    try:
        hojas = leer_hojas(archivo)
    except Exception:
        return {"ok": False, "mensaje": "No se pudo leer el archivo. Verifica que sea un Excel válido."}
    if not hojas:
        return {"ok": False, "mensaje": "No se reconoce el formato: no se encontró la fila de encabezados "
                                        "(Id del Empleado, Fecha, Hora, Tipo de Marcación)."}

    faltan = [texto for campo, texto in OBLIGATORIOS.items() if campo not in hojas[0][3]]
    if faltan:
        return {"ok": False, "mensaje": "Faltan columnas obligatorias: " + ", ".join(faltan) + "."}

    formato = "HOJA_UNICA" if len(hojas) == 1 else "HOJA_POR_COLABORADOR"
    id_imp = importacion_repo.crear(db, id_usuario, archivo.filename, formato)

    incidencias, validos, vistos = [], [], set()
    leidos = 0
    for nombre_hoja, df, fila_enc, mapa in hojas:
        prefijo = f"Hoja {nombre_hoja}, " if formato == "HOJA_POR_COLABORADOR" else ""
        for i in range(fila_enc + 1, len(df)):
            fila = df.iloc[i].tolist()
            if all(_vacio(v) for v in fila):
                continue
            leidos += 1
            n_fila = i + 1
            dato = {campo: (None if _vacio(fila[col]) else str(fila[col]).strip()) for campo, col in mapa.items()}

            vacios = [OBLIGATORIOS[c] for c in OBLIGATORIOS if not dato.get(c)]
            if vacios:
                incidencias.append((n_fila, "INCOMPLETO", f"{prefijo}fila {n_fila}: falta {', '.join(vacios)}"))
                continue
            fecha, hora = _fecha(dato["fecha"]), _hora(dato["hora"])
            if not fecha or not hora:
                campo = "Fecha" if not fecha else "Hora"
                incidencias.append((n_fila, "INCOMPLETO", f"{prefijo}fila {n_fila}: {campo} no válida ({dato[campo.lower()]})"))
                continue

            id_col = _id_texto(dato["id"])
            clave = (id_col, fecha, hora)
            if clave in vistos or asistencia_repo.existe(db, *clave):
                incidencias.append((n_fila, "DUPLICADO", f"{prefijo}fila {n_fila}: {dato.get('nombres') or id_col} ({id_col}) ya tiene una marcación el {_dma(fecha)} a las {hora}"))
                continue
            vistos.add(clave)
            validos.append({
                "id": id_col, "nombres": dato.get("nombres") or f"Colaborador {id_col}",
                "id_depto": _id_texto(dato["id_depto"]) if dato.get("id_depto") else None,
                "depto": dato.get("depto"), "id_cargo": dato.get("id_cargo"),
                "fecha": fecha, "hora": hora, "tipo": dato["tipo_marcacion"].capitalize(),
                "forma": dato.get("forma"), "fuente": dato.get("fuente"),
            })

    # RF-02-1 / RF-02-2: registrar o actualizar colaboradores y departamentos
    for v in validos:
        if v["id_depto"] and v["depto"]:
            colaborador_repo.guardar_departamento(db, int(v["id_depto"]), v["depto"].title())
        colaborador_repo.guardar(db, v["id"], v["nombres"].title(), int(v["id_depto"]) if v["id_depto"] else None, v["id_cargo"])

    # RF-01-7: almacenar registros válidos
    asistencia_repo.insertar_lote(db, id_imp, validos)

    # RF-01-6: inconsistencias por colaborador y día
    nombres = {v["id"]: v["nombres"].title() for v in validos}
    dias = sorted({(v["id"], v["fecha"]) for v in validos})
    for id_col, fecha in dias:
        tipos = asistencia_repo.tipos_del_dia(db, id_col, fecha)
        repetido = any(a == b for a, b in zip(tipos, tipos[1:]))
        if len(tipos) % 2 == 1 or repetido or (tipos and tipos[0] != "Entrada"):
            incidencias.append((None, "INCONSISTENTE",
                                f"{nombres[id_col]} ({id_col}), {_dma(fecha)}: {' → '.join(tipos)}. "
                                + ("Falta una marcación de salida." if len(tipos) % 2 == 1 else "Hay marcaciones del mismo tipo seguidas.")))

    errores = sum(1 for inc in incidencias if inc[1] != "INCONSISTENTE")
    inconsistentes = len(incidencias) - errores
    if not validos:
        resultado = "FALLIDA"
    elif incidencias:
        resultado = "CON OBSERVACIONES"
    else:
        resultado = "EXITOSA"

    importacion_repo.guardar_incidencias(db, id_imp, incidencias)
    importacion_repo.cerrar(db, id_imp, leidos, len(validos), errores, resultado)
    auditoria_repo.registrar(db, id_usuario, "IMPORTACION",
                             f"{archivo.filename}: {len(validos)} cargados, {errores} con error, {inconsistentes} inconsistencias ({resultado})")
    db.commit()

    return {
        "ok": bool(validos), "id_importacion": id_imp, "resultado": resultado, "formato": formato,
        "leidos": leidos, "cargados": len(validos), "errores": errores, "inconsistentes": inconsistentes,
        "colaboradores": len({v["id"] for v in validos}),
        "mensaje": f"Se cargaron {len(validos)} de {leidos} marcaciones.",
    }
