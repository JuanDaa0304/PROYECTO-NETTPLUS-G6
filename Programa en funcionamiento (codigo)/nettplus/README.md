# NettPlus · Sistema de gestión y análisis de asistencia

Aplicación web para NetPlus que importa los reportes de marcaciones de **Z-BioTime**, valida los datos,
guarda el historial de asistencia y genera el parte diario. Proyecto del Grupo 6, Sprint 2.

## Cómo ejecutarlo

```bash
# 1. Crear y activar un entorno virtual (una sola vez)
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
python run.py
```

Abrir **http://127.0.0.1:5000**. La base de datos se crea sola en `data/nettplus.db`.

| Usuario | Contraseña | Rol |
| --- | --- | --- |
| admin | admin123 | Asistente de RR.HH. (carga archivos) |
| jefe | jefe123 | Jefe de área |
| contabilidad | conta123 | Contabilidad |
| desarrollo | desarrollo123 | Desarrollo organizacional |

Para probar, sube `data/ejemplos/marcaciones_demo_hoja_unica.xlsx` en **Carga de marcaciones**.
Ese archivo trae datos ficticios del 21 oct al 20 nov 2026 y algunos errores a propósito
(un duplicado, una fila sin fecha y días con entrada sin salida). Se regenera con
`python data/ejemplos/generar_demo.py`.

Pruebas unitarias: `python -m pytest`

## Arquitectura

**Aplicación web monolítica con arquitectura en capas, siguiendo el patrón MVC** (Modelo-Vista-Controlador),
construida con Flask.

```
 Navegador (HTML + CSS + JS)
        │  petición HTTP
        ▼
 ┌─────────────────────────────┐
 │ Vista        templates/     │  Plantillas Jinja2: lo que ve el usuario
 ├─────────────────────────────┤
 │ Controlador  routes/        │  Blueprints de Flask: reciben la petición, revisan el rol
 ├─────────────────────────────┤
 │ Servicios    services/      │  Reglas de negocio: validar Excel, atrasos, corte 21–20
 ├─────────────────────────────┤
 │ Repositorios repositories/  │  Consultas SQL (acceso a datos)
 ├─────────────────────────────┤
 │ Base de datos  SQLite       │  data/nettplus.db
 └─────────────────────────────┘
```

Cada capa solo habla con la de abajo. Por ejemplo, la carga de un Excel sigue este camino:
`routes/importacion.py` → `services/importacion_service.py` → `repositories/*` → SQLite.

## Estructura de carpetas

```
nettplus/
├── run.py                      Punto de entrada
├── requirements.txt            Dependencias
├── app/
│   ├── __init__.py             Fábrica de la aplicación (create_app)
│   ├── config.py               Configuración (BD, límites, hora de entrada)
│   ├── db.py                   Conexión y esquema de la base de datos
│   ├── seguridad.py            Sesión, inactividad y menú por rol
│   ├── routes/                 Controladores (un Blueprint por módulo)
│   │   ├── auth.py             M5 Iniciar / cerrar sesión
│   │   ├── panel.py            Inicio
│   │   ├── importacion.py      M1 Carga y registro de cargas
│   │   ├── personal.py         M2 Colaboradores
│   │   ├── marcaciones.py      M2 Historial de asistencia
│   │   ├── informes.py         M4 Parte diario
│   │   └── sistema.py          Opciones del Sprint 3
│   ├── services/               Lógica de negocio
│   │   ├── importacion_service.py
│   │   ├── asistencia_service.py
│   │   └── periodo.py          Periodo de corte 21–20
│   ├── repositories/           Acceso a datos (SQL)
│   ├── templates/              Vistas HTML (Jinja2), una carpeta por módulo
│   └── static/                 CSS, JavaScript e imágenes (logos oficiales)
├── data/
│   ├── nettplus.db             Base de datos (se crea al ejecutar)
│   └── ejemplos/               Excel de prueba con el formato de Z-BioTime
└── tests/                      Pruebas unitarias (pytest)
```

## Tecnologías

| Capa | Tecnología | Para qué |
| --- | --- | --- |
| Backend | Python 3 + **Flask 3** | Servidor web, rutas, sesiones, Blueprints |
| Lectura de Excel | **pandas** + **openpyxl** (xlrd para .xls) | Leer el reporte de Z-BioTime |
| Base de datos | **SQLite** | Base relacional en un archivo, sin instalar un servidor |
| Seguridad | **Werkzeug** (incluido en Flask) | Contraseñas con hash; sesión con cierre a los 15 min |
| Frontend | **HTML5 + Jinja2**, **CSS3** propio, **JavaScript** simple | Interfaz sin frameworks pesados |
| Diseño | Colores del Manual de Marca Nettplus; fuente Figtree | Identidad visual corporativa |
| Pruebas | **pytest** | Pruebas unitarias de reglas y pantallas |

## Base de datos

Las tablas siguen el diagrama de clases de Enterprise Architect: `usuarios`, `roles`, `colaboradores`,
`departamentos`, `importaciones`, `registros_asistencia` (una fila por marcación), `incidencias_importacion`
y `eventos_auditoria`.

> La versión anterior guardaba cada Excel completo como texto JSON en una sola tabla, por eso
> `netplus.db` llegó a pesar 673 MB. Esa base ya no se usa y se puede borrar.

## Requisitos implementados en el Sprint 2

| Módulo | Requisitos |
| --- | --- |
| M1 Importación | RF-01-1 cargar Excel · RF-01-2 formato · RF-01-3 campos obligatorios · RF-01-4 duplicados · RF-01-5 incompletos · RF-01-6 inconsistencias · RF-01-7 guardar · RF-01-8 registrar resultado |
| M2 Colaboradores | RF-02-1 / RF-02-2 registrar colaborador y departamento · RF-02-3 listado · RF-02-4 búsqueda · RF-02-5 / RF-02-6 / RF-02-7 historial |
| M4 Informes | RF-04-1 parte diario |
| M5 Seguridad | RF-05-1 iniciar sesión · RF-05-2 cerrar sesión (y por inactividad) · RF-05-3 menú y permisos por rol · RF-05-6 eventos de auditoría |

Pendiente para el Sprint 3: indicadores, cierre de periodo, exportar a Excel/PDF, importar permisos y horarios,
cuentas y roles, correcciones y consulta de trazabilidad.
