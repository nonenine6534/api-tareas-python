"""
routes/tareas.py — Endpoints del recurso "tareas"
====================================================

Cada función atiende una ruta de la API. Todas trabajan con la
conexión a SQLite que inyecta la dependencia obtener_bd().

Códigos de estado que se usan:
    200  OK                  -> lecturas y actualizaciones
    201  Created             -> tarea creada (POST)
    204  No Content          -> tarea eliminada (DELETE)
    404  Not Found           -> el id no existe
    422  Unprocessable Entity-> el JSON no pasa las validaciones
                                (lo genera FastAPI solo)

Las consultas SQL usan parámetros con "?" (nunca se pegan los
datos del usuario dentro del texto SQL): así se evitan las
inyecciones SQL.
"""

import sqlite3
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ..database import obtener_bd
from ..models import (
    PaginaTareas,
    TareaActualizar,
    TareaCrear,
    TareaParcial,
    TareaRespuesta,
)

# Todas las rutas de este archivo empiezan por /tareas
router = APIRouter(prefix="/tareas", tags=["tareas"])


def fila_a_tarea(fila: sqlite3.Row) -> TareaRespuesta:
    """Convierte una fila de SQLite en el modelo de respuesta.

    En la tabla, "completada" se guarda como entero (0/1) porque
    SQLite no tiene tipo booleano; aquí pasa a True/False.
    """
    return TareaRespuesta(
        id=fila["id"],
        titulo=fila["titulo"],
        descripcion=fila["descripcion"],
        completada=bool(fila["completada"]),
        creada_en=fila["creada_en"],
    )


def buscar_fila(bd: sqlite3.Connection, tarea_id: int) -> sqlite3.Row:
    """Devuelve la fila de una tarea o lanza un error 404."""
    fila = bd.execute(
        "SELECT * FROM tareas WHERE id = ?", (tarea_id,)
    ).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return fila


# ------------------------------------------------------------------
# Listar tareas (con paginación y filtros)
# ------------------------------------------------------------------

@router.get("", response_model=PaginaTareas)
def listar_tareas(
    limite: int = Query(default=10, ge=1, le=100,
                        description="Máximo de tareas por página"),
    desplazamiento: int = Query(default=0, ge=0,
                                description="Tareas a saltar (para la página siguiente)"),
    completada: Optional[bool] = Query(default=None,
                                       description="Filtrar por completadas o pendientes"),
    buscar: Optional[str] = Query(default=None,
                                  description="Texto a buscar en el título"),
    bd: sqlite3.Connection = Depends(obtener_bd),
):
    """Lista las tareas paginadas, con filtros opcionales.

    Ejemplo: /tareas?limite=5&desplazamiento=5&completada=false
    """
    # Se construye el WHERE solo con los filtros que llegan.
    condiciones: list[str] = []
    parametros: list = []

    if completada is not None:
        condiciones.append("completada = ?")
        parametros.append(1 if completada else 0)
    if buscar:
        condiciones.append("titulo LIKE ?")
        parametros.append(f"%{buscar}%")

    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

    # Total de tareas que cumplen los filtros (para la respuesta)
    total = bd.execute(
        f"SELECT COUNT(*) AS n FROM tareas {where}", parametros
    ).fetchone()["n"]

    # La página pedida: LIMIT = cuántas, OFFSET = desde cuál
    filas = bd.execute(
        f"SELECT * FROM tareas {where} ORDER BY id LIMIT ? OFFSET ?",
        [*parametros, limite, desplazamiento],
    ).fetchall()

    return PaginaTareas(
        total=total,
        limite=limite,
        desplazamiento=desplazamiento,
        resultados=[fila_a_tarea(fila) for fila in filas],
    )


# ------------------------------------------------------------------
# Obtener una tarea
# ------------------------------------------------------------------

@router.get("/{tarea_id}", response_model=TareaRespuesta)
def obtener_tarea(tarea_id: int, bd: sqlite3.Connection = Depends(obtener_bd)):
    """Devuelve una tarea por su id, o un error 404 si no existe."""
    return fila_a_tarea(buscar_fila(bd, tarea_id))


# ------------------------------------------------------------------
# Crear una tarea
# ------------------------------------------------------------------

@router.post("", response_model=TareaRespuesta, status_code=201)
def crear_tarea(datos: TareaCrear, bd: sqlite3.Connection = Depends(obtener_bd)):
    """Crea una tarea nueva y la devuelve con su id asignado."""
    cursor = bd.execute(
        "INSERT INTO tareas (titulo, descripcion, completada) VALUES (?, ?, ?)",
        (datos.titulo, datos.descripcion, 1 if datos.completada else 0),
    )
    bd.commit()
    # lastrowid es el id que SQLite acaba de generar
    return fila_a_tarea(buscar_fila(bd, cursor.lastrowid))


# ------------------------------------------------------------------
# Actualizar una tarea (completa con PUT, parcial con PATCH)
# ------------------------------------------------------------------

@router.put("/{tarea_id}", response_model=TareaRespuesta)
def actualizar_tarea(tarea_id: int, datos: TareaActualizar,
                     bd: sqlite3.Connection = Depends(obtener_bd)):
    """Reemplaza TODOS los datos de la tarea indicada."""
    buscar_fila(bd, tarea_id)  # si no existe, responde 404
    bd.execute(
        "UPDATE tareas SET titulo = ?, descripcion = ?, completada = ? WHERE id = ?",
        (datos.titulo, datos.descripcion, 1 if datos.completada else 0, tarea_id),
    )
    bd.commit()
    return fila_a_tarea(buscar_fila(bd, tarea_id))


@router.patch("/{tarea_id}", response_model=TareaRespuesta)
def actualizar_parcial(tarea_id: int, datos: TareaParcial,
                       bd: sqlite3.Connection = Depends(obtener_bd)):
    """Actualiza SOLO los campos que el cliente envía.

    exclude_unset=True deja fuera los campos que no vinieron en
    el JSON, para no sobrescribirlos con None por accidente.
    """
    buscar_fila(bd, tarea_id)  # si no existe, responde 404

    cambios = datos.model_dump(exclude_unset=True)
    if cambios:
        # Las claves vienen del modelo de Pydantic (son nombres
        # de columna seguros); los valores van como parámetros.
        if "completada" in cambios:
            cambios["completada"] = 1 if cambios["completada"] else 0
        columnas = ", ".join(f"{campo} = ?" for campo in cambios)
        bd.execute(
            f"UPDATE tareas SET {columnas} WHERE id = ?",
            [*cambios.values(), tarea_id],
        )
        bd.commit()

    return fila_a_tarea(buscar_fila(bd, tarea_id))


# ------------------------------------------------------------------
# Eliminar una tarea
# ------------------------------------------------------------------

@router.delete("/{tarea_id}", status_code=204)
def borrar_tarea(tarea_id: int, bd: sqlite3.Connection = Depends(obtener_bd)):
    """Elimina la tarea indicada (204: éxito sin contenido)."""
    buscar_fila(bd, tarea_id)  # si no existe, responde 404
    bd.execute("DELETE FROM tareas WHERE id = ?", (tarea_id,))
    bd.commit()
    return None  # con 204 no se devuelve cuerpo
