"""
API de Tareas con FastAPI
=========================

API REST pequeña para gestionar una lista de tareas (CRUD completo).
Las tareas se guardan en memoria (un diccionario), así que se pierden
al detener el servidor: es un proyecto de práctica, sin base de datos.

Cómo ejecutarla:
    1. Instala las dependencias:  pip install -r requirements.txt
    2. Arranca el servidor:       uvicorn main:app --reload
    3. Abre la documentación automática que genera FastAPI:
       http://127.0.0.1:8000/docs

Endpoints:
    GET    /tareas            -> lista todas las tareas
    GET    /tareas/{id}       -> una tarea por su id
    POST   /tareas            -> crea una tarea nueva
    PUT    /tareas/{id}       -> actualiza una tarea completa
    DELETE /tareas/{id}       -> elimina una tarea
"""

from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# ------------------------------------------------------------------
# Modelos de datos (Pydantic valida los JSON que llegan a la API)
# ------------------------------------------------------------------

class TareaEntrada(BaseModel):
    """Datos que el cliente envía al crear o actualizar una tarea."""
    titulo: str
    descripcion: Optional[str] = None
    completada: bool = False


class Tarea(TareaEntrada):
    """Tarea tal como la devuelve la API: los datos más su id."""
    id: int


# ------------------------------------------------------------------
# Aplicación y "base de datos" en memoria
# ------------------------------------------------------------------

app = FastAPI(
    title="API de Tareas",
    description="API REST sencilla para gestionar tareas (CRUD en memoria).",
    version="1.0.0",
)

# Diccionario id -> Tarea. Hace de base de datos temporal.
tareas: dict[int, Tarea] = {}
siguiente_id = 1


def _crear(titulo: str, descripcion: Optional[str], completada: bool) -> Tarea:
    """Función auxiliar: asigna el siguiente id y guarda la tarea."""
    global siguiente_id
    tarea = Tarea(id=siguiente_id, titulo=titulo,
                  descripcion=descripcion, completada=completada)
    tareas[tarea.id] = tarea
    siguiente_id += 1
    return tarea


# Dos tareas de ejemplo para que la API no empiece vacía
_crear("Estudiar FastAPI", "Repasar rutas y modelos de Pydantic", False)
_crear("Hacer la práctica de programación", None, True)


# ------------------------------------------------------------------
# Endpoints (rutas de la API)
# ------------------------------------------------------------------

@app.get("/")
def inicio():
    """Ruta raíz: mensaje de bienvenida."""
    return {"mensaje": "API de Tareas funcionando. Visita /docs para la documentación."}


@app.get("/tareas", response_model=list[Tarea])
def listar_tareas():
    """Devuelve todas las tareas."""
    return list(tareas.values())


@app.get("/tareas/{tarea_id}", response_model=Tarea)
def obtener_tarea(tarea_id: int):
    """Devuelve una tarea por su id, o un error 404 si no existe."""
    if tarea_id not in tareas:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tareas[tarea_id]


@app.post("/tareas", response_model=Tarea, status_code=201)
def crear_tarea(datos: TareaEntrada):
    """Crea una tarea nueva a partir del JSON recibido."""
    return _crear(datos.titulo, datos.descripcion, datos.completada)


@app.put("/tareas/{tarea_id}", response_model=Tarea)
def actualizar_tarea(tarea_id: int, datos: TareaEntrada):
    """Reemplaza por completo la tarea indicada."""
    if tarea_id not in tareas:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    tarea = Tarea(id=tarea_id, titulo=datos.titulo,
                  descripcion=datos.descripcion, completada=datos.completada)
    tareas[tarea_id] = tarea
    return tarea


@app.delete("/tareas/{tarea_id}")
def borrar_tarea(tarea_id: int):
    """Elimina la tarea indicada."""
    if tarea_id not in tareas:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    del tareas[tarea_id]
    return {"mensaje": f"Tarea {tarea_id} eliminada"}
