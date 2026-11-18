"""
main.py — Atajo de arranque
=============================

La aplicación vive en el paquete "app" (app/main.py). Este
archivo solo la reexporta para poder arrancar también con:

    uvicorn main:app --reload
"""

from app.main import app

__all__ = ["app"]
