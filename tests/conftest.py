"""
tests/conftest.py — Preparación común de las pruebas
======================================================

pytest ejecuta este archivo ANTES que las pruebas. Aquí se
hacen dos cosas:

1. Apuntar la API a una base de datos TEMPORAL (variable de
   entorno TAREAS_DB), para que las pruebas nunca toquen los
   datos reales de tareas.db.
2. Definir la fixture "cliente": un TestClient de FastAPI que
   permite llamar a la API como si fuera un navegador, pero
   sin arrancar el servidor. Antes de cada prueba se vacía la
   tabla para que cada una empiece desde cero.
"""

import os
import tempfile

# IMPORTANTE: la variable debe definirse antes de importar la
# app, porque database.py lee la ruta al cargarse el módulo.
os.environ["TAREAS_DB"] = os.path.join(tempfile.mkdtemp(), "pruebas.db")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import crear_tablas, obtener_conexion  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def cliente():
    """Devuelve un cliente de pruebas con la tabla vacía."""
    crear_tablas()
    conexion = obtener_conexion()
    conexion.execute("DELETE FROM tareas")
    conexion.commit()
    conexion.close()
    return TestClient(app)


@pytest.fixture()
def crear(cliente):
    """Atajo: crea una tarea de ejemplo y devuelve su JSON."""
    respuesta = cliente.post(
        "/tareas",
        json={"titulo": "Tarea de ejemplo", "descripcion": "Para las pruebas"},
    )
    return respuesta.json()
