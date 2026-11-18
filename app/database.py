"""
database.py — Conexión con la base de datos SQLite
====================================================

Aquí vive todo lo relacionado con la base de datos:

- La ruta del archivo .db (se puede cambiar con la variable de
  entorno TAREAS_DB; las pruebas la usan para trabajar con una
  base temporal y no tocar la de verdad).
- crear_tablas(): crea la tabla "tareas" si todavía no existe.
- obtener_bd(): dependencia de FastAPI que abre una conexión
  para cada petición y la cierra al terminar.

Se usa el módulo sqlite3 de la librería estándar de Python:
no hace falta instalar nada más para guardar datos.
"""

import os
import sqlite3

# Ruta del archivo de base de datos. Por defecto, "tareas.db"
# junto a la carpeta del proyecto. Las pruebas definen la
# variable de entorno TAREAS_DB con una ruta temporal.
RUTA_BD = os.environ.get(
    "TAREAS_DB",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tareas.db"),
)


def obtener_conexion() -> sqlite3.Connection:
    """Abre una conexión nueva con la base de datos.

    row_factory = sqlite3.Row permite acceder a las columnas
    por nombre (fila["titulo"]) en vez de por posición.
    """
    conexion = sqlite3.connect(RUTA_BD)
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_tablas() -> None:
    """Crea la tabla de tareas si no existe (se llama al arrancar)."""
    conexion = obtener_conexion()
    conexion.execute(
        """
        CREATE TABLE IF NOT EXISTS tareas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo      TEXT    NOT NULL,
            descripcion TEXT,
            completada  INTEGER NOT NULL DEFAULT 0,
            creada_en   TEXT    NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conexion.commit()
    conexion.close()


def obtener_bd():
    """Dependencia de FastAPI: una conexión por petición.

    El 'yield' entrega la conexión a la ruta; cuando la ruta
    termina, el código después del yield la cierra. Así ninguna
    petición deja la base de datos abierta.
    """
    conexion = obtener_conexion()
    try:
        yield conexion
    finally:
        conexion.close()
