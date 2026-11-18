"""
app/main.py — Punto de entrada de la aplicación
==================================================

Aquí se crea la aplicación FastAPI, se preparan las tablas de
la base de datos y se conectan las rutas de cada recurso.

Para arrancar el servidor (desde la carpeta del proyecto):

    uvicorn app.main:app --reload

Y la documentación automática queda en http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

from .database import crear_tablas
from .routes import tareas

app = FastAPI(
    title="API de Tareas",
    description=(
        "API REST para gestionar tareas: CRUD completo con "
        "persistencia en SQLite, paginación, filtros y validaciones."
    ),
    version="2.0.0",
)

# Al importar la app se asegura que la tabla exista.
# (En un proyecto grande esto se haría con migraciones;
# para practicar, CREATE TABLE IF NOT EXISTS es suficiente.)
crear_tablas()

# Se conectan las rutas del recurso "tareas"
app.include_router(tareas.router)


@app.get("/", tags=["inicio"])
def inicio():
    """Ruta raíz: mensaje de bienvenida y enlace a la documentación."""
    return {
        "mensaje": "API de Tareas funcionando.",
        "documentacion": "/docs",
        "version": app.version,
    }
