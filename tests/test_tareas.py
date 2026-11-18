"""
tests/test_tareas.py — Pruebas automáticas de la API
======================================================

Cada función test_* comprueba un comportamiento de la API.
Se ejecutan con:

    pytest

Si todas pasan, el programa imprime un resumen en verde.
Las pruebas usan el cliente y los datos de conftest.py, así
que trabajan sobre una base de datos temporal y vacía.
"""


def test_crear_tarea(cliente):
    """POST /tareas crea la tarea y responde 201 con su id."""
    respuesta = cliente.post(
        "/tareas",
        json={"titulo": "Estudiar FastAPI", "descripcion": "Capítulo de rutas"},
    )
    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["id"] >= 1
    assert datos["titulo"] == "Estudiar FastAPI"
    assert datos["completada"] is False  # valor por defecto


def test_crear_tarea_invalida_devuelve_422(cliente):
    """Sin título (o con título vacío) Pydantic responde 422."""
    assert cliente.post("/tareas", json={}).status_code == 422
    assert cliente.post("/tareas", json={"titulo": ""}).status_code == 422


def test_listar_tareas_empieza_vacio(cliente):
    """GET /tareas sin datos: total 0 y lista de resultados vacía."""
    datos = cliente.get("/tareas").json()
    assert datos["total"] == 0
    assert datos["resultados"] == []


def test_obtener_tarea_y_error_404(cliente, crear):
    """GET /tareas/{id} devuelve la tarea; un id falso da 404."""
    respuesta = cliente.get(f"/tareas/{crear['id']}")
    assert respuesta.status_code == 200
    assert respuesta.json()["titulo"] == "Tarea de ejemplo"

    assert cliente.get("/tareas/99999").status_code == 404


def test_actualizar_tarea_completa_put(cliente, crear):
    """PUT reemplaza todos los campos de la tarea."""
    respuesta = cliente.put(
        f"/tareas/{crear['id']}",
        json={"titulo": "Título nuevo", "descripcion": None, "completada": True},
    )
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["titulo"] == "Título nuevo"
    assert datos["descripcion"] is None
    assert datos["completada"] is True


def test_actualizar_parcial_patch(cliente, crear):
    """PATCH solo cambia lo enviado: el título se mantiene."""
    respuesta = cliente.patch(
        f"/tareas/{crear['id']}", json={"completada": True}
    )
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["completada"] is True
    assert datos["titulo"] == "Tarea de ejemplo"  # no se tocó


def test_eliminar_tarea(cliente, crear):
    """DELETE responde 204 y la tarea deja de existir."""
    assert cliente.delete(f"/tareas/{crear['id']}").status_code == 204
    assert cliente.get(f"/tareas/{crear['id']}").status_code == 404
    # Borrar dos veces la misma tarea también es un 404
    assert cliente.delete(f"/tareas/{crear['id']}").status_code == 404


def test_paginacion(cliente):
    """El listado respeta limite y desplazamiento, y da el total."""
    for numero in range(5):
        cliente.post("/tareas", json={"titulo": f"Tarea {numero}"})

    pagina1 = cliente.get("/tareas", params={"limite": 2, "desplazamiento": 0}).json()
    assert pagina1["total"] == 5
    assert len(pagina1["resultados"]) == 2

    pagina3 = cliente.get("/tareas", params={"limite": 2, "desplazamiento": 4}).json()
    assert len(pagina3["resultados"]) == 1  # solo queda la quinta


def test_filtro_por_completada(cliente):
    """El filtro completada=true solo trae las tareas hechas."""
    cliente.post("/tareas", json={"titulo": "Pendiente"})
    cliente.post("/tareas", json={"titulo": "Hecha", "completada": True})

    datos = cliente.get("/tareas", params={"completada": True}).json()
    assert datos["total"] == 1
    assert datos["resultados"][0]["titulo"] == "Hecha"
