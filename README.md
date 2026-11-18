# API de Tareas — Python con FastAPI

API REST construida con **FastAPI** para gestionar una lista de tareas
(CRUD completo), con **persistencia real en SQLite**, validaciones con
**Pydantic**, **paginación**, filtros y **pruebas automáticas con pytest**.

A diferencia de la primera versión (que guardaba todo en un diccionario
en memoria), las tareas ahora sobreviven al reinicio del servidor porque
quedan guardadas en un archivo de base de datos `tareas.db`.

## Características

- CRUD completo: crear, leer, actualizar (PUT y PATCH) y eliminar tareas.
- Persistencia en **SQLite** con el módulo `sqlite3` de la librería
  estándar (sin ORM: SQL escrito a mano y con parámetros, anti-inyección).
- Validaciones automáticas con Pydantic: título obligatorio de 1 a 120
  caracteres, descripción de hasta 500, etc. Lo inválido responde **422**.
- **Paginación** en el listado (`limite` y `desplazamiento`) con el
  total de resultados.
- Filtros en el listado: por estado (`completada`) y por texto en el
  título (`buscar`).
- Códigos HTTP correctos: 200, **201** al crear, **204** al eliminar,
  **404** si el id no existe, **422** si el JSON no valida.
- Estructura profesional en paquetes: la app, la base de datos, los
  modelos y las rutas viven en archivos separados.
- 9 pruebas automáticas con **pytest** sobre una base de datos temporal.

## Endpoints

| Método | Ruta            | Descripción                                   | Respuesta |
|--------|-----------------|-----------------------------------------------|-----------|
| GET    | `/`             | Mensaje de bienvenida                         | 200       |
| GET    | `/tareas`       | Lista paginada de tareas (con filtros)        | 200       |
| GET    | `/tareas/{id}`  | Devuelve una tarea por su id                  | 200 / 404 |
| POST   | `/tareas`       | Crea una tarea nueva                          | 201 / 422 |
| PUT    | `/tareas/{id}`  | Reemplaza la tarea completa                   | 200 / 404 |
| PATCH  | `/tareas/{id}`  | Actualiza solo los campos enviados            | 200 / 404 |
| DELETE | `/tareas/{id}`  | Elimina la tarea                              | 204 / 404 |

Parámetros del listado (`GET /tareas`):

| Parámetro        | Por defecto | Descripción                              |
|------------------|-------------|------------------------------------------|
| `limite`         | 10          | Máximo de tareas por página (1–100)      |
| `desplazamiento` | 0           | Cuántas tareas saltar (página siguiente) |
| `completada`     | —           | `true` o `false` para filtrar por estado |
| `buscar`         | —           | Texto a buscar dentro del título         |

La respuesta del listado es un objeto con `total`, `limite`,
`desplazamiento` y `resultados` (la página de tareas).

## Tecnologías

- **Python 3.10+**
- **FastAPI** — el framework web; genera la documentación OpenAPI sola.
- **Pydantic** — modelos y validación de los datos de entrada/salida.
- **SQLite** (`sqlite3`, librería estándar) — persistencia en un archivo.
- **Uvicorn** — servidor ASGI.
- **pytest** + **TestClient** (con `httpx`) — pruebas automáticas.

## Cómo ejecutarla

```bash
# (Opcional) Crear y activar un entorno virtual
python -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Arrancar el servidor
uvicorn app.main:app --reload
```

La API queda en http://127.0.0.1:8000 y la **documentación interactiva**
en http://127.0.0.1:8000/docs (desde ahí se pueden probar los endpoints).

La base de datos se crea sola la primera vez (`tareas.db`). Para usar
otra ruta, define la variable de entorno `TAREAS_DB` antes de arrancar.

## Ejemplos de uso con curl

```bash
# Listar la primera página de tareas
curl "http://127.0.0.1:8000/tareas?limite=5&desplazamiento=0"

# Listar solo las pendientes que contengan "estudiar" en el título
curl "http://127.0.0.1:8000/tareas?completada=false&buscar=estudiar"

# Crear una tarea nueva
curl -X POST http://127.0.0.1:8000/tareas \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Estudiar para el examen", "descripcion": "Tema 3: APIs REST"}'

# Ver una tarea por su id
curl http://127.0.0.1:8000/tareas/1

# Marcarla como completada (actualización parcial, PATCH)
curl -X PATCH http://127.0.0.1:8000/tareas/1 \
  -H "Content-Type: application/json" \
  -d '{"completada": true}'

# Actualizarla por completo (PUT)
curl -X PUT http://127.0.0.1:8000/tareas/1 \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Estudiar para el examen", "descripcion": "Temas 3 y 4", "completada": false}'

# Eliminar una tarea
curl -X DELETE http://127.0.0.1:8000/tareas/1
```

## Cómo correr las pruebas

```bash
pytest            # ejecuta todas las pruebas de tests/
pytest -v         # lo mismo, mostrando el nombre de cada prueba
```

Las pruebas usan una base de datos temporal (no tocan `tareas.db`) y
cubren: crear, validación 422, listado vacío, obtener y 404, PUT, PATCH,
DELETE (204 y 404 posterior), paginación y el filtro por completadas.

## Estructura del proyecto

```
api-tareas-python/
├── app/
│   ├── __init__.py
│   ├── main.py          # crea la app, prepara las tablas, conecta rutas
│   ├── database.py      # conexión SQLite, crear tablas, dependencia
│   ├── models.py        # esquemas Pydantic (crear, actualizar, respuesta…)
│   └── routes/
│       ├── __init__.py
│       └── tareas.py    # endpoints del recurso "tareas"
├── tests/
│   ├── conftest.py      # BD temporal y fixtures de pytest
│   └── test_tareas.py   # 9 pruebas de la API
├── main.py              # atajo: permite "uvicorn main:app"
├── requirements.txt     # dependencias (API + pruebas)
└── README.md
```

## Qué practica este proyecto

- Diseño de una **API REST** de verdad: recursos, verbos HTTP y códigos
  de estado usados con criterio (201, 204, 404, 422).
- **Separación de responsabilidades**: rutas, modelos y base de datos en
  módulos distintos, como en un proyecto profesional.
- **Inyección de dependencias** de FastAPI (`Depends`) para entregar una
  conexión de base de datos a cada petición.
- SQL con **parámetros** (`?`) para evitar inyecciones, y paginación con
  `LIMIT`/`OFFSET`.
- Diferencia entre **PUT** (reemplazo completo) y **PATCH** (parcial,
  con `exclude_unset`).
- **Pruebas automáticas** con pytest y fixtures: la API se verifica sin
  arrancar el servidor y sin tocar los datos reales.
