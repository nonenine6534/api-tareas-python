# API de Tareas — Python con FastAPI

API REST pequeña construida con **FastAPI** para gestionar una lista de
tareas (CRUD completo). Las tareas se guardan **en memoria** (un
diccionario), así que se pierden al detener el servidor: es un proyecto
de práctica, sin base de datos.

## Endpoints

| Método   | Ruta            | Descripción                    |
|----------|-----------------|--------------------------------|
| GET      | `/`             | Mensaje de bienvenida          |
| GET      | `/tareas`       | Lista todas las tareas         |
| GET      | `/tareas/{id}`  | Devuelve una tarea por su id   |
| POST     | `/tareas`       | Crea una tarea nueva (201)     |
| PUT      | `/tareas/{id}`  | Actualiza una tarea completa   |
| DELETE   | `/tareas/{id}`  | Elimina una tarea              |

Si el id no existe, la API responde con un error **404**.

## Cómo ejecutarla

Requisitos: **Python 3.10 o superior**.

```bash
# (Opcional) Crear y activar un entorno virtual
python -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Arrancar el servidor
uvicorn main:app --reload
```

La API queda en http://127.0.0.1:8000 y FastAPI genera la
**documentación interactiva** automáticamente en
http://127.0.0.1:8000/docs (desde ahí se pueden probar los endpoints).

## Ejemplos de uso con curl

```bash
# Listar todas las tareas
curl http://127.0.0.1:8000/tareas

# Crear una tarea nueva
curl -X POST http://127.0.0.1:8000/tareas \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Estudiar para el examen", "descripcion": "Tema 3: APIs REST"}'

# Ver una tarea por su id
curl http://127.0.0.1:8000/tareas/1

# Actualizar una tarea completa
curl -X PUT http://127.0.0.1:8000/tareas/1 \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Estudiar para el examen", "completada": true}'

# Eliminar una tarea
curl -X DELETE http://127.0.0.1:8000/tareas/1
```

## Estructura del proyecto

```
api-tareas-python/
├── main.py           # toda la API: modelos, datos en memoria y rutas
├── requirements.txt  # dependencias (fastapi y uvicorn)
└── README.md
```

## Tecnologías y conceptos usados

- **FastAPI** y **Pydantic**: los modelos (`TareaEntrada`, `Tarea`)
  validan automáticamente los JSON que llegan a la API.
- **Uvicorn** como servidor ASGI.
- Códigos de estado HTTP correctos: 200, 201 y 404 con
  `HTTPException`.
- Documentación automática con OpenAPI/Swagger en `/docs`.
