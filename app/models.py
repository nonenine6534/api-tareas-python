"""
models.py — Modelos de datos (esquemas) con Pydantic
======================================================

Los modelos describen la FORMA de los datos que entran y salen
de la API. Pydantic los valida automáticamente: si un JSON no
cumple las reglas (por ejemplo, un título vacío), FastAPI
responde con un error 422 sin que escribamos esa comprobación.

Hay modelos separados para crear, actualizar y responder,
porque no es lo mismo lo que el cliente envía (sin id) que lo
que la API devuelve (con id y fecha de creación).
"""

from typing import Optional

from pydantic import BaseModel, Field


class TareaCrear(BaseModel):
    """Datos que el cliente envía al CREAR una tarea (POST)."""

    # Field(...) define las validaciones del campo:
    # el título es obligatorio, de 1 a 120 caracteres.
    titulo: str = Field(min_length=1, max_length=120)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    completada: bool = False


class TareaActualizar(BaseModel):
    """Datos para la actualización COMPLETA de una tarea (PUT).

    En un PUT el cliente reenvía la tarea entera, así que los
    campos y validaciones son los mismos que al crear.
    """

    titulo: str = Field(min_length=1, max_length=120)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    completada: bool = False


class TareaParcial(BaseModel):
    """Datos para la actualización PARCIAL de una tarea (PATCH).

    Todos los campos son opcionales: el cliente solo envía los
    que quiere cambiar, por ejemplo {"completada": true}.
    """

    titulo: Optional[str] = Field(default=None, min_length=1, max_length=120)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    completada: Optional[bool] = None


class TareaRespuesta(BaseModel):
    """Tarea tal como la devuelve la API: con id y fecha."""

    id: int
    titulo: str
    descripcion: Optional[str] = None
    completada: bool
    creada_en: str


class PaginaTareas(BaseModel):
    """Respuesta paginada del listado de tareas.

    Además de la página de resultados, incluye el total para
    que el cliente sepa cuántas tareas hay en conjunto.
    """

    total: int
    limite: int
    desplazamiento: int
    resultados: list[TareaRespuesta]
