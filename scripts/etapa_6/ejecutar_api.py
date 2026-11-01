from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    api,
    create_task,
    date_offset,
    ensure_server,
    error_detail,
    json_body,
    list_tasks,
    make_result,
    reset_server_db,
    save_json,
    upload,
)


def post(payload: dict):
    response = api("POST", "/api/tasks", payload)
    return response, json_body(response)


def move(task_id, payload: dict):
    response = api("PATCH", f"/api/tasks/{task_id}/move", payload)
    return response, json_body(response)


def put(task_id, payload: dict):
    response = api("PUT", f"/api/tasks/{task_id}", payload)
    return response, json_body(response)


def add_subtask(task_id, payload: dict):
    response = api("POST", f"/api/tasks/{task_id}/subtasks", payload)
    return response, json_body(response)


def patch_subtask(subtask_id, payload: dict):
    response = api("PATCH", f"/api/subtasks/{subtask_id}", payload)
    return response, json_body(response)


def only_task(task_id: int):
    return next((item for item in list_tasks() if item["id"] == task_id), None)


def list_tags() -> list[str]:
    response = api("GET", "/api/tags")
    response.raise_for_status()
    return response.json()


# --- Crear tarea (CP-CRE-01 a CP-CRE-09) -----------------------------------


def cp_cre_01() -> dict:
    reset_server_db()
    response, body = post({"title": "Preparar informe"})
    tasks = list_tasks()
    appears = isinstance(body, dict) and any(
        item["id"] == body.get("id") for item in tasks
    )
    checks = {
        "HTTP 201": response.status_code == 201,
        "id entero": isinstance(body.get("id"), int),
        "título correcto": body.get("title") == "Preparar informe",
        "descripción vacía": body.get("description") == "",
        "estado Pendiente": body.get("status") == "Pendiente",
        "due_date nula": body.get("due_date") is None,
        "position 0": body.get("position") == 0,
        "overdue falso": body.get("overdue") is False,
        "subtask_total 0": body.get("subtask_total") == 0,
        "subtasks vacías": body.get("subtasks") == [],
        "attachments vacíos": body.get("attachments") == [],
        "aparece en el listado": appears,
    }
    obtained = (
        f"HTTP 201; tarea #{body.get('id')} creada en estado Pendiente, "
        f"position 0 y overdue falso, presente en el listado"
    )
    return make_result(
        "CP-CRE-01",
        checks,
        obtained,
        "Alta típica; verifica RF2 y la forma completa de la respuesta.",
        body,
    )


def cp_cre_02() -> dict:
    reset_server_db()
    response, body = post({"title": "A"})
    checks = {
        "HTTP 201": response.status_code == 201,
        "título de un carácter": body.get("title") == "A",
        "estado Pendiente": body.get("status") == "Pendiente",
    }
    obtained = "HTTP 201; título de un carácter aceptado con estado Pendiente"
    return make_result(
        "CP-CRE-02", checks, obtained, "Valor límite inferior válido del título.", body
    )


def cp_cre_03() -> dict:
    reset_server_db()
    response, body = post({"title": "a" * 100})
    checks = {
        "HTTP 201": response.status_code == 201,
        "título de 100 caracteres": isinstance(body.get("title"), str)
        and len(body["title"]) == 100,
        "estado Pendiente": body.get("status") == "Pendiente",
    }
    obtained = "HTTP 201; título de exactamente 100 caracteres aceptado"
    return make_result(
        "CP-CRE-03", checks, obtained, "Valor límite superior válido del título.", body
    )


def cp_cre_04() -> dict:
    reset_server_db()
    response, body = post({"title": "a" * 101})
    tasks = list_tasks()
    detail = error_detail(body)
    checks = {
        "HTTP 422": response.status_code == 422,
        "mensaje de longitud": "100" in detail,
        "listado vacío": tasks == [],
    }
    obtained = "HTTP 422; título de 101 caracteres rechazado y listado vacío"
    return make_result(
        "CP-CRE-04", checks, obtained, "Valor límite superior inválido.", body
    )


def cp_cre_05() -> dict:
    reset_server_db()
    response, body = post({"title": ""})
    tasks = list_tasks()
    detail = error_detail(body)
    checks = {
        "HTTP 422": response.status_code == 422,
        "mensaje de título vacío": "vacío" in detail,
        "listado vacío": tasks == [],
    }
    obtained = "HTTP 422; título vacío rechazado y listado vacío"
    return make_result(
        "CP-CRE-05", checks, obtained, "Clase de equivalencia inválida.", body
    )


def cp_cre_06() -> dict:
    reset_server_db()
    response, body = post({"title": "     "})
    tasks = list_tasks()
    detail = error_detail(body)
    checks = {
        "HTTP 422": response.status_code == 422,
        "mensaje de título vacío": "vacío" in detail,
        "listado vacío": tasks == [],
    }
    obtained = "HTTP 422; título con solo espacios rechazado y listado vacío"
    return make_result(
        "CP-CRE-06",
        checks,
        obtained,
        "Clase inválida y límite inferior tras recortar.",
        body,
    )


def cp_cre_07() -> dict:
    reset_server_db()
    response, body = post({"title": "  Revisar pruebas  "})
    tasks = list_tasks()
    checks = {
        "HTTP 201": response.status_code == 201,
        "título recortado": body.get("title") == "Revisar pruebas",
        "estado Pendiente": body.get("status") == "Pendiente",
        "persistencia recortada": any(
            item.get("title") == "Revisar pruebas" for item in tasks
        ),
    }
    obtained = (
        "HTTP 201; espacios externos recortados y título persistido "
        'como "Revisar pruebas"'
    )
    return make_result(
        "CP-CRE-07", checks, obtained, "Clase válida con normalización.", body
    )


def cp_cre_08() -> dict:
    reset_server_db()
    due = date_offset(7)
    response, body = post(
        {
            "title": "Informe final",
            "description": "Detalle de la tarea",
            "due_date": due,
        }
    )
    checks = {
        "HTTP 201": response.status_code == 201,
        "descripción almacenada": body.get("description") == "Detalle de la tarea",
        "fecha almacenada": body.get("due_date") == due,
        "overdue falso": body.get("overdue") is False,
    }
    obtained = (
        f"HTTP 201; descripción y fecha límite ({due}) almacenadas y overdue falso"
    )
    return make_result(
        "CP-CRE-08", checks, obtained, "Alta con descripción y fecha futura.", body
    )


def cp_cre_09() -> dict:
    reset_server_db()
    response, body = post({"title": "Tarea atrasada", "due_date": date_offset(-1)})
    tasks = list_tasks()
    detail = error_detail(body)
    checks = {
        "HTTP 422": response.status_code == 422,
        "mensaje de fecha": "anterior a hoy" in detail,
        "listado vacío": tasks == [],
    }
    obtained = "HTTP 422; fecha límite pasada rechazada al crear y listado vacío"
    return make_result(
        "CP-CRE-09", checks, obtained, "Valor límite inválido de fecha al crear.", body
    )


# --- Mover y reordenar (CP-MOV-01 a CP-MOV-05) -----------------------------


def cp_mov_01() -> dict:
    reset_server_db()
    task = create_task("Mover a Terminada")
    r1, b1 = move(task["id"], {"status": "En curso"})
    r2, b2 = move(task["id"], {"status": "Terminada"})
    stored = only_task(task["id"])
    checks = {
        "En curso HTTP 200": r1.status_code == 200,
        "En curso aplicado": b1.get("status") == "En curso",
        "Terminada HTTP 200": r2.status_code == 200,
        "Terminada aplicada": b2.get("status") == "Terminada",
        "id y título sin cambios": stored.get("id") == task["id"]
        and stored.get("title") == task["title"],
        "persistido Terminada": stored.get("status") == "Terminada",
    }
    obtained = (
        "Tres estados válidos: PATCH 200 a En curso y a Terminada, "
        'con estado final "Terminada" persistido'
    )
    return make_result(
        "CP-MOV-01",
        checks,
        obtained,
        "Transición completa entre los tres estados.",
        stored,
    )


def cp_mov_02() -> dict:
    reset_server_db()
    task = create_task("Estado inválido")
    bad_status, _ = move(task["id"], {"status": "Finalizada"})
    bad_position, _ = move(task["id"], {"status": "Pendiente", "position": -1})
    stored = only_task(task["id"])
    checks = {
        "estado inválido HTTP 422": bad_status.status_code == 422,
        "posición inválida HTTP 422": bad_position.status_code == 422,
        "estado conservado": stored.get("status") == "Pendiente",
        "posición conservada": stored.get("position") == 0,
    }
    obtained = (
        "HTTP 422 con estado y con posición inválidos; la tarea conservó su "
        "estado Pendiente y su posición 0"
    )
    return make_result(
        "CP-MOV-02", checks, obtained, "Clase inválida de estado y de posición.", stored
    )


def cp_mov_03() -> dict:
    reset_server_db()
    response, body = move(999999, {"status": "En curso"})
    checks = {
        "HTTP 404": response.status_code == 404,
        "detalle Tarea no encontrada": body.get("detail") == "Tarea no encontrada",
    }
    obtained = 'HTTP 404 con detalle "Tarea no encontrada"'
    return make_result(
        "CP-MOV-03",
        checks,
        obtained,
        "Movimiento sobre un identificador inexistente.",
        body,
    )


def cp_mov_04() -> dict:
    reset_server_db()
    response, body = move("abc", {"status": "En curso"})
    checks = {
        "HTTP 422": response.status_code == 422,
        "error de validación": isinstance(body, dict) and "detail" in body,
    }
    obtained = "HTTP 422 por identificador no numérico en la ruta"
    return make_result(
        "CP-MOV-04", checks, obtained, "Clase inválida de identificador.", body
    )


def cp_mov_05() -> dict:
    reset_server_db()
    first = create_task("A")
    create_task("B")
    third = create_task("C")
    response, body = move(third["id"], {"status": "Pendiente", "position": 0})
    tasks = list_tasks()
    order = [item["title"] for item in tasks]
    positions = [item["position"] for item in tasks]
    checks = {
        "HTTP 200": response.status_code == 200,
        "orden C, A, B": order == ["C", "A", "B"],
        "posiciones 0, 1, 2": positions == [0, 1, 2],
        "id movido correcto": body.get("id") == third["id"],
        "primer id sin cambios": first["id"] in [item["id"] for item in tasks],
    }
    obtained = (
        f"HTTP 200; la columna quedó ordenada como C, A, B con posiciones {positions}"
    )
    return make_result(
        "CP-MOV-05", checks, obtained, "Reordenamiento sin cambio de estado.", tasks
    )


# --- Editar tarea (CP-EDI-01 a CP-EDI-03) ----------------------------------


def cp_edi_01() -> dict:
    reset_server_db()
    task = create_task("Tarea original", description="Original")
    due = date_offset(3)
    response, body = put(
        task["id"],
        {"title": "Tarea editada", "description": "Nueva descripción", "due_date": due},
    )
    checks = {
        "HTTP 200": response.status_code == 200,
        "título actualizado": body.get("title") == "Tarea editada",
        "descripción actualizada": body.get("description") == "Nueva descripción",
        "fecha actualizada": body.get("due_date") == due,
        "id sin cambios": body.get("id") == task["id"],
        "estado sin cambios": body.get("status") == "Pendiente",
    }
    obtained = (
        "PUT 200; título, descripción y fecha límite actualizados sin alterar el estado"
    )
    return make_result("CP-EDI-01", checks, obtained, "Flujo normal de edición.", body)


def cp_edi_02() -> dict:
    reset_server_db()
    response, body = put(999999, {"title": "Tarea fantasma"})
    checks = {
        "HTTP 404": response.status_code == 404,
        "detalle Tarea no encontrada": body.get("detail") == "Tarea no encontrada",
    }
    obtained = 'HTTP 404 con detalle "Tarea no encontrada"'
    return make_result(
        "CP-EDI-02",
        checks,
        obtained,
        "Edición sobre un identificador inexistente.",
        body,
    )


def cp_edi_03() -> dict:
    reset_server_db()
    task = create_task("Con fecha futura", due_date=date_offset(5))
    past = date_offset(-2)
    response, body = put(task["id"], {"title": "Revisar informe", "due_date": past})
    checks = {
        "HTTP 200": response.status_code == 200,
        "fecha pasada almacenada": body.get("due_date") == past,
        "overdue verdadero": body.get("overdue") is True,
    }
    obtained = (
        f"HTTP 200; la edición admitió la fecha pasada ({past}) "
        "y overdue quedó verdadero"
    )
    return make_result(
        "CP-EDI-03",
        checks,
        obtained,
        "La restricción de fecha futura aplica solo al alta.",
        body,
    )


# --- Checklist de subtareas (CP-SUB-01 a CP-SUB-04) ------------------------


def cp_sub_01() -> dict:
    reset_server_db()
    task = create_task("Con checklist")
    response, body = add_subtask(task["id"], {"title": "Diseñar casos"})
    checks = {
        "HTTP 201": response.status_code == 201,
        "subtask_total 1": body.get("subtask_total") == 1,
        "subtask_done 0": body.get("subtask_done") == 0,
        "título de la subtarea": body.get("subtasks", [{}])[0].get("title")
        == "Diseñar casos",
    }
    obtained = "HTTP 201; subtarea creada, subtask_total 1 y subtask_done 0"
    return make_result(
        "CP-SUB-01", checks, obtained, "Flujo normal de alta de subtarea.", body
    )


def cp_sub_02() -> dict:
    reset_server_db()
    task = create_task("Marcar subtarea")
    _, created = add_subtask(task["id"], {"title": "Paso"})
    subtask_id = created["subtasks"][0]["id"]

    r1, marked = patch_subtask(subtask_id, {"done": True})
    r2, unmarked = patch_subtask(subtask_id, {"done": False})
    checks = {
        "marcar HTTP 200": r1.status_code == 200,
        "subtask_done 1": marked.get("subtask_done") == 1,
        "desmarcar HTTP 200": r2.status_code == 200,
        "subtask_done 0": unmarked.get("subtask_done") == 0,
        "estado de la tarea sin cambios": unmarked.get("status") == "Pendiente",
    }
    obtained = (
        "HTTP 200 en ambos PATCH; el avance pasó a 1/1 y volvió a 0/1 "
        "sin cambiar el estado"
    )
    return make_result(
        "CP-SUB-02",
        checks,
        obtained,
        "Marcado y desmarcado de una subtarea.",
        {"marked": marked, "unmarked": unmarked},
    )


def cp_sub_03() -> dict:
    reset_server_db()
    task = create_task("Eliminar subtarea")
    _, created = add_subtask(task["id"], {"title": "Paso"})
    subtask_id = created["subtasks"][0]["id"]
    response = api("DELETE", f"/api/subtasks/{subtask_id}")
    body = response.text
    stored = only_task(task["id"])
    checks = {
        "HTTP 204": response.status_code == 204,
        "sin cuerpo": body == "",
        "subtask_total 0": stored.get("subtask_total") == 0,
    }
    obtained = "DELETE 204 sin cuerpo; la tarea quedó con subtask_total 0"
    return make_result(
        "CP-SUB-03",
        checks,
        obtained,
        "Flujo normal de eliminación de subtarea.",
        stored,
    )


def cp_sub_04() -> dict:
    reset_server_db()
    response, body = add_subtask(999999, {"title": "Subtarea huérfana"})
    checks = {
        "HTTP 404": response.status_code == 404,
        "detalle Tarea no encontrada": body.get("detail") == "Tarea no encontrada",
    }
    obtained = 'HTTP 404 con detalle "Tarea no encontrada"'
    return make_result(
        "CP-SUB-04",
        checks,
        obtained,
        "Alta de subtarea sobre una tarea inexistente.",
        body,
    )


# --- Control de finalización (CP-BLO-01 a CP-BLO-04) -----------------------


def cp_blo_01() -> dict:
    reset_server_db()
    task = create_task("Bloquear finalización")
    add_subtask(task["id"], {"title": "Pendiente 1"})
    response, body = move(task["id"], {"status": "Terminada"})
    stored = only_task(task["id"])
    checks = {
        "HTTP 409": response.status_code == 409,
        "detalle con 1 subtarea": body.get("detail")
        == "No se puede finalizar: la tarea tiene 1 subtarea pendiente",
        "estado conservado": stored.get("status") == "Pendiente",
    }
    obtained = "HTTP 409 con detalle del bloqueo; la tarea conservó su estado Pendiente"
    return make_result(
        "CP-BLO-01", checks, obtained, "Regla de bloqueo al finalizar.", stored
    )


def cp_blo_02() -> dict:
    reset_server_db()
    task = create_task("Finalizar permitida")
    add_subtask(task["id"], {"title": "Hecha", "done": True})
    response, body = move(task["id"], {"status": "Terminada"})
    checks = {
        "HTTP 200": response.status_code == 200,
        "estado Terminada": body.get("status") == "Terminada",
    }
    obtained = "HTTP 200; tarea finalizada al no tener subtareas pendientes"
    return make_result("CP-BLO-02", checks, obtained, "Complemento del bloqueo.", body)


def cp_blo_03() -> dict:
    reset_server_db()
    task = create_task("Terminada y reabierta")
    move(task["id"], {"status": "Terminada"})
    response, body = add_subtask(task["id"], {"title": "Tarea adicional"})
    checks = {
        "HTTP 201": response.status_code == 201,
        "subtarea creada": body.get("subtask_total") == 1,
        "estado En curso": body.get("status") == "En curso",
    }
    obtained = 'HTTP 201 con la subtarea creada y la tarea reabierta a "En curso"'
    return make_result(
        "CP-BLO-03",
        checks,
        obtained,
        "Reapertura al agregar una subtarea pendiente.",
        body,
    )


def cp_blo_04() -> dict:
    reset_server_db()
    task = create_task("Desmarcar reabre")
    _, created = add_subtask(task["id"], {"title": "Paso", "done": True})
    subtask_id = created["subtasks"][0]["id"]
    move(task["id"], {"status": "Terminada"})
    response, body = patch_subtask(subtask_id, {"done": False})
    checks = {
        "HTTP 200": response.status_code == 200,
        "subtarea desmarcada": body.get("subtask_done") == 0,
        "estado En curso": body.get("status") == "En curso",
    }
    obtained = 'HTTP 200 con la subtarea desmarcada y la tarea reabierta a "En curso"'
    return make_result(
        "CP-BLO-04", checks, obtained, "Reapertura al desmarcar una subtarea.", body
    )


# --- Fecha límite y vencimiento (CP-FEC-01 y CP-FEC-02) --------------------


def cp_fec_01() -> dict:
    reset_server_db()
    task = create_task("Con vencimiento", due_date=date_offset(2))
    before = only_task(task["id"])
    _, after = put(
        task["id"], {"title": "Con vencimiento", "due_date": date_offset(-2)}
    )
    checks = {
        "overdue falso al crear": before.get("overdue") is False,
        "overdue verdadero tras editar": after.get("overdue") is True,
        "estado sin cambios": after.get("status") == "Pendiente",
    }
    obtained = (
        "overdue pasó de falso a verdadero al editar la fecha, sin cambiar el estado"
    )
    return make_result(
        "CP-FEC-01",
        checks,
        obtained,
        "El vencimiento se deriva y no se almacena.",
        after,
    )


def cp_fec_02() -> dict:
    reset_server_db()
    future = create_task("Con fecha futura", due_date=date_offset(10))
    overdue = create_task("Con fecha pasada")
    put(overdue["id"], {"title": "Con fecha pasada", "due_date": date_offset(-1)})
    response = api("GET", "/api/tasks?overdue=true")
    filtered = response.json()
    all_tasks = list_tasks()
    checks = {
        "filtro HTTP 200": response.status_code == 200,
        "solo la vencida": [item["id"] for item in filtered] == [overdue["id"]],
        "sin filtro devuelve dos": len(all_tasks) == 2,
        "ambas presentes": {item["id"] for item in all_tasks}
        == {future["id"], overdue["id"]},
    }
    obtained = (
        "El filtro overdue devolvió solo la tarea vencida y el listado completo las dos"
    )
    return make_result(
        "CP-FEC-02",
        checks,
        obtained,
        "Verifica el parámetro de consulta de vencidas.",
        {"filtered": filtered},
    )


# --- Archivos adjuntos (CP-ADJ-01 a CP-ADJ-06) -----------------------------


def cp_adj_01() -> dict:
    reset_server_db()
    task = create_task("Con adjunto")
    response = upload(task["id"], "notas.txt", b"x" * 1024)
    body = json_body(response)
    attachment = (body.get("attachments") or [{}])[0]
    checks = {
        "HTTP 201": response.status_code == 201,
        "un adjunto": len(body.get("attachments") or []) == 1,
        "nombre original": attachment.get("filename") == "notas.txt",
        "tamaño 1024": attachment.get("size_bytes") == 1024,
    }
    obtained = 'HTTP 201; adjunto "notas.txt" de 1024 bytes agregado a la tarea'
    return make_result(
        "CP-ADJ-01", checks, obtained, "Subida con extensión permitida.", body
    )


def cp_adj_02() -> dict:
    reset_server_db()
    task = create_task("Descargar adjunto")
    content = "contenido de prueba".encode("utf-8")
    upload(task["id"], "notas.txt", content)
    stored = only_task(task["id"])
    attachment_id = stored["attachments"][0]["id"]
    response = api("GET", f"/api/tasks/{task['id']}/attachments/{attachment_id}")
    disposition = response.headers.get("content-disposition", "")
    checks = {
        "HTTP 200": response.status_code == 200,
        "contenido idéntico": response.content == content,
        "nombre original en la cabecera": "notas.txt" in disposition,
    }
    obtained = (
        "HTTP 200 con el contenido idéntico al subido y el nombre original "
        "en la cabecera"
    )
    return make_result(
        "CP-ADJ-02",
        checks,
        obtained,
        "Verifica la integridad del archivo almacenado.",
        disposition,
    )


def cp_adj_03() -> dict:
    reset_server_db()
    task = create_task("Eliminar adjunto")
    upload(task["id"], "notas.txt", b"contenido")
    stored = only_task(task["id"])
    attachment_id = stored["attachments"][0]["id"]
    response = api("DELETE", f"/api/tasks/{task['id']}/attachments/{attachment_id}")
    after = only_task(task["id"])
    download = api("GET", f"/api/tasks/{task['id']}/attachments/{attachment_id}")
    checks = {
        "HTTP 204": response.status_code == 204,
        "tarea sin adjuntos": after.get("attachments") == [],
        "descarga posterior 404": download.status_code == 404,
    }
    obtained = (
        "DELETE 204; la tarea quedó sin adjuntos y la descarga posterior respondió 404"
    )
    return make_result(
        "CP-ADJ-03",
        checks,
        obtained,
        "Verifica también que el archivo físico deja de estar disponible.",
        after,
    )


def cp_adj_04() -> dict:
    reset_server_db()
    task = create_task("Extensión inválida")
    response = upload(task["id"], "programa.exe", b"binario")
    body = json_body(response)
    detail = error_detail(body)
    stored = only_task(task["id"])
    checks = {
        "HTTP 415": response.status_code == 415,
        "detalle de formatos aceptados": "Se aceptan" in detail,
        "tarea sin adjuntos": stored.get("attachments") == [],
    }
    obtained = (
        "HTTP 415 con el detalle de los formatos aceptados; la tarea quedó sin adjuntos"
    )
    return make_result(
        "CP-ADJ-04", checks, obtained, "Clase inválida de extensión.", detail
    )


def cp_adj_05() -> dict:
    reset_server_db()
    task = create_task("Archivo muy grande")
    content = b"x" * (5 * 1024 * 1024 + 1)
    response = upload(task["id"], "grande.txt", content)
    body = json_body(response)
    detail = error_detail(body)
    stored = only_task(task["id"])
    checks = {
        "HTTP 413": response.status_code == 413,
        "detalle de tamaño": detail == "El archivo supera el tamaño máximo de 5 MB",
        "tarea sin adjuntos": stored.get("attachments") == [],
    }
    obtained = (
        'HTTP 413 con el detalle "El archivo supera el tamaño máximo de 5 MB"; '
        "sin adjuntos"
    )
    return make_result(
        "CP-ADJ-05", checks, obtained, "Valor límite superior de tamaño.", detail
    )


def cp_adj_06() -> dict:
    reset_server_db()
    task = create_task("Límite de adjuntos")
    for index in range(1, 4):
        upload(task["id"], f"archivo{index}.txt", b"contenido")
    response = upload(task["id"], "cuarto.txt", b"contenido")
    body = json_body(response)
    detail = error_detail(body)
    stored = only_task(task["id"])
    checks = {
        "HTTP 409": response.status_code == 409,
        "detalle del límite": "3 archivos adjuntos" in detail,
        "conserva 3 adjuntos": len(stored.get("attachments") or []) == 3,
    }
    obtained = (
        "HTTP 409 con el detalle del límite; la tarea conservó exactamente 3 adjuntos"
    )
    return make_result(
        "CP-ADJ-06", checks, obtained, "Valor límite superior de cantidad.", detail
    )


# --- Eliminar y restaurar (CP-ELI-01, CP-ELI-02, CP-RES-01, CP-RES-02) -----


def cp_eli_01() -> dict:
    reset_server_db()
    task = create_task("Eliminar esta tarea")
    response = api("DELETE", f"/api/tasks/{task['id']}")
    body = response.text
    tasks = list_tasks()
    checks = {
        "HTTP 204": response.status_code == 204,
        "sin cuerpo": body == "",
        "tarea ausente del listado": all(item["id"] != task["id"] for item in tasks),
    }
    obtained = "DELETE 204 sin cuerpo; la tarea dejó de aparecer en el listado"
    return make_result(
        "CP-ELI-01",
        checks,
        obtained,
        "Eliminación lógica de una tarea existente.",
        tasks,
    )


def cp_eli_02() -> dict:
    reset_server_db()
    response = api("DELETE", "/api/tasks/999999")
    body = json_body(response)
    checks = {
        "HTTP 404": response.status_code == 404,
        "detalle Tarea no encontrada": body.get("detail") == "Tarea no encontrada",
    }
    obtained = 'HTTP 404 con detalle "Tarea no encontrada"'
    return make_result(
        "CP-ELI-02",
        checks,
        obtained,
        "Eliminación sobre un identificador inexistente.",
        body,
    )


def cp_res_01() -> dict:
    reset_server_db()
    task = create_task("Restaurar esta tarea")
    api("DELETE", f"/api/tasks/{task['id']}")
    response = api("POST", f"/api/tasks/{task['id']}/restore")
    body = json_body(response)
    tasks = list_tasks()
    checks = {
        "HTTP 200": response.status_code == 200,
        "tarea restaurada": body.get("id") == task["id"],
        "presente en el listado": any(item["id"] == task["id"] for item in tasks),
    }
    obtained = "HTTP 200; la tarea eliminada volvió a estar presente en el listado"
    return make_result(
        "CP-RES-01", checks, obtained, "Flujo normal de restauración.", body
    )


def cp_res_02() -> dict:
    reset_server_db()
    task = create_task("Tarea activa")
    response = api("POST", f"/api/tasks/{task['id']}/restore")
    body = json_body(response)
    checks = {
        "HTTP 404": response.status_code == 404,
        "detalle Tarea no encontrada": body.get("detail") == "Tarea no encontrada",
    }
    obtained = 'HTTP 404 con detalle "Tarea no encontrada"'
    return make_result(
        "CP-RES-02",
        checks,
        obtained,
        "La restauración solo aplica a tareas eliminadas.",
        body,
    )


# --- Listar tareas y persistencia (CP-LIS-01) ------------------------------


def cp_lis_01() -> dict:
    reset_server_db()
    empty = list_tasks()
    first = create_task("Primera tarea")
    second = create_task("Segunda tarea")
    third = create_task("Tercera tarea")
    tasks = list_tasks()
    ids = [item["id"] for item in tasks]
    keys = {
        "id",
        "title",
        "description",
        "status",
        "due_date",
        "position",
        "created_at",
        "overdue",
        "subtask_total",
        "subtask_done",
        "subtasks",
        "attachments",
    }
    checks = {
        "listado vacío": empty == [],
        "tres tareas": len(tasks) == 3,
        "orden de creación": ids == [first["id"], second["id"], third["id"]],
        "ids ascendentes": ids == sorted(ids),
        "campos completos": all(keys <= set(item) for item in tasks),
        "todas Pendiente": all(item["status"] == "Pendiente" for item in tasks),
        "posiciones 0, 1, 2": [item["position"] for item in tasks] == [0, 1, 2],
    }
    obtained = (
        "El primer listado fue vacío y el segundo contuvo las tres tareas "
        "en orden de creación"
    )
    return make_result(
        "CP-LIS-01",
        checks,
        obtained,
        "Verifica el listado y la persistencia en SQLite.",
        tasks,
    )


# --- Prioridad (CP-PRI-01 a CP-PRI-04) -------------------------------------


def cp_pri_01() -> dict:
    reset_server_db()
    response, body = post({"title": "Tarea prioritaria", "priority": "Alta"})
    checks = {
        "HTTP 201": response.status_code == 201,
        "prioridad Alta": body.get("priority") == "Alta",
        "título correcto": body.get("title") == "Tarea prioritaria",
    }
    obtained = 'HTTP 201; la tarea se creó con priority "Alta"'
    return make_result(
        "CP-PRI-01",
        checks,
        obtained,
        "Clase válida de prioridad con un valor extremo del conjunto.",
        body,
    )


def cp_pri_02() -> dict:
    reset_server_db()
    response, body = post({"title": "Tarea sin prioridad"})
    checks = {
        "HTTP 201": response.status_code == 201,
        "prioridad por defecto Media": body.get("priority") == "Media",
    }
    obtained = 'HTTP 201; al omitir priority la tarea quedó con "Media"'
    return make_result(
        "CP-PRI-02",
        checks,
        obtained,
        "Clase válida por omisión del campo priority.",
        body,
    )


def cp_pri_03() -> dict:
    reset_server_db()
    response, body = post({"title": "Prioridad inválida", "priority": "Urgente"})
    tasks = list_tasks()
    detail = error_detail(body)
    checks = {
        "HTTP 422": response.status_code == 422,
        "mensaje de prioridad": "prioridad" in detail.lower(),
        "listado vacío": tasks == [],
    }
    obtained = "HTTP 422; prioridad fuera del conjunto rechazada y listado sin cambios"
    return make_result(
        "CP-PRI-03", checks, obtained, "Clase inválida de prioridad.", body
    )


def cp_pri_04() -> dict:
    reset_server_db()
    task = create_task("Cambiar prioridad")
    response, body = put(task["id"], {"title": task["title"], "priority": "Baja"})
    actions = [entry.get("action") for entry in body.get("activity", [])]
    stored = only_task(task["id"])
    checks = {
        "HTTP 200": response.status_code == 200,
        "prioridad Baja": body.get("priority") == "Baja",
        "persistida Baja": stored.get("priority") == "Baja",
        "actividad de prioridad": "Prioridad cambiada a Baja" in actions,
    }
    obtained = 'PUT 200; prioridad "Baja" aplicada y registrada en la actividad'
    return make_result(
        "CP-PRI-04",
        checks,
        obtained,
        "Actualización de la prioridad con registro en el historial.",
        body,
    )


# --- Responsable (CP-ASG-01 a CP-ASG-03) -----------------------------------


def cp_asg_01() -> dict:
    reset_server_db()
    response, body = post(
        {"title": "Responsable con espacios", "assignee": "  Ana Gómez  "}
    )
    checks = {
        "HTTP 201": response.status_code == 201,
        "responsable recortado": body.get("assignee") == "Ana Gómez",
    }
    obtained = 'HTTP 201; los espacios externos se recortaron a "Ana Gómez"'
    return make_result(
        "CP-ASG-01", checks, obtained, "Clase válida con normalización.", body
    )


def cp_asg_02() -> dict:
    reset_server_db()
    response, body = post({"title": "Responsable largo", "assignee": "a" * 61})
    tasks = list_tasks()
    detail = error_detail(body)
    checks = {
        "HTTP 422": response.status_code == 422,
        "mensaje de responsable": "responsable" in detail.lower(),
        "listado vacío": tasks == [],
    }
    obtained = "HTTP 422; responsable de 61 caracteres rechazado y listado sin cambios"
    return make_result(
        "CP-ASG-02",
        checks,
        obtained,
        "Valor límite superior inválido del responsable.",
        body,
    )


def cp_asg_03() -> dict:
    reset_server_db()
    task = create_task("Asignar responsable")
    response, body = put(task["id"], {"title": task["title"], "assignee": "Luis"})
    actions = [entry.get("action") for entry in body.get("activity", [])]
    stored = only_task(task["id"])
    checks = {
        "HTTP 200": response.status_code == 200,
        "responsable Luis": body.get("assignee") == "Luis",
        "persistido": stored.get("assignee") == "Luis",
        "actividad de responsable": "Responsable asignado a Luis" in actions,
    }
    obtained = 'PUT 200; responsable "Luis" asignado y registrado en la actividad'
    return make_result(
        "CP-ASG-03",
        checks,
        obtained,
        "Actualización del responsable con registro en el historial.",
        body,
    )


# --- Etiquetas (CP-TAG-01 a CP-TAG-04) -------------------------------------


def cp_tag_01() -> dict:
    reset_server_db()
    response, body = post({"title": "Tarea etiquetada", "tags": ["backend", "pruebas"]})
    tags = list_tags()
    checks = {
        "HTTP 201": response.status_code == 201,
        "etiquetas en la respuesta": sorted(body.get("tags") or [])
        == ["backend", "pruebas"],
        "backend en el catálogo": "backend" in tags,
        "pruebas en el catálogo": "pruebas" in tags,
    }
    obtained = "HTTP 201; las dos etiquetas quedaron en la tarea y en /api/tags"
    return make_result(
        "CP-TAG-01", checks, obtained, "Clase válida de etiquetas.", body
    )


def cp_tag_02() -> dict:
    reset_server_db()
    response, body = post(
        {"title": "Demasiadas etiquetas", "tags": ["a", "b", "c", "d", "e", "f"]}
    )
    detail = error_detail(body)
    checks = {
        "HTTP 409": response.status_code == 409,
        "mensaje del límite": "5 etiquetas" in detail,
        "listado vacío": list_tasks() == [],
    }
    obtained = "HTTP 409 con el detalle del límite; no se creó ninguna tarea"
    return make_result(
        "CP-TAG-02",
        checks,
        obtained,
        "Valor límite superior inválido de etiquetas.",
        body,
    )


def cp_tag_03() -> dict:
    reset_server_db()
    empty, empty_body = post({"title": "Etiqueta vacía", "tags": [""]})
    spaces, _ = post({"title": "Etiqueta con espacios", "tags": ["   "]})
    detail = error_detail(empty_body)
    checks = {
        "vacía HTTP 422": empty.status_code == 422,
        "solo espacios HTTP 422": spaces.status_code == 422,
        "mensaje de etiqueta": "etiqueta" in detail.lower(),
        "listado vacío": list_tasks() == [],
    }
    obtained = "HTTP 422 con la etiqueta vacía y con la de solo espacios"
    return make_result(
        "CP-TAG-03",
        checks,
        obtained,
        "Clase inválida y valor límite inferior de la etiqueta.",
        empty_body,
    )


def cp_tag_04() -> dict:
    reset_server_db()
    task = create_task("Reemplazar etiquetas")
    put(task["id"], {"title": task["title"], "tags": ["uno", "dos"]})
    response, body = put(task["id"], {"title": task["title"], "tags": ["dos", "tres"]})
    actions = [entry.get("action") for entry in body.get("activity", [])]
    checks = {
        "HTTP 200": response.status_code == 200,
        "etiquetas reemplazadas": sorted(body.get("tags") or []) == ["dos", "tres"],
        "actividad de eliminación": "Etiqueta eliminada: uno" in actions,
        "actividad de alta": "Etiqueta agregada: tres" in actions,
    }
    obtained = (
        'PUT 200; se quitó "uno", se agregó "tres" y ambas acciones '
        "quedaron registradas"
    )
    return make_result(
        "CP-TAG-04",
        checks,
        obtained,
        "Reemplazo completo de etiquetas con registro en el historial.",
        body,
    )


# --- Enlaces (CP-ENL-01 a CP-ENL-04) ---------------------------------------


def cp_enl_01() -> dict:
    reset_server_db()
    response, body = post(
        {
            "title": "Tarea con enlace",
            "links": [{"url": "https://ejemplo.com/doc", "label": "Documento"}],
        }
    )
    links = body.get("links") or []
    first = links[0] if links else {}
    checks = {
        "HTTP 201": response.status_code == 201,
        "un enlace": len(links) == 1,
        "url correcta": first.get("url") == "https://ejemplo.com/doc",
        "label correcto": first.get("label") == "Documento",
    }
    obtained = "HTTP 201; el enlace https quedó persistido con su nombre"
    return make_result(
        "CP-ENL-01", checks, obtained, "Clase válida de enlace https.", body
    )


def cp_enl_02() -> dict:
    reset_server_db()
    ftp, ftp_body = post(
        {"title": "Enlace ftp", "links": [{"url": "ftp://ejemplo.com"}]}
    )
    plain, _ = post({"title": "Enlace sin esquema", "links": [{"url": "ejemplo.com"}]})
    detail = error_detail(ftp_body)
    checks = {
        "ftp HTTP 422": ftp.status_code == 422,
        "sin esquema HTTP 422": plain.status_code == 422,
        "mensaje de enlace": "http" in detail.lower(),
        "listado vacío": list_tasks() == [],
    }
    obtained = "HTTP 422 con ftp:// y con una url sin esquema"
    return make_result(
        "CP-ENL-02", checks, obtained, "Clase inválida de esquema del enlace.", ftp_body
    )


def cp_enl_03() -> dict:
    reset_server_db()
    links = [{"url": f"https://ejemplo.com/{index}"} for index in range(1, 7)]
    response, body = post({"title": "Demasiados enlaces", "links": links})
    detail = error_detail(body)
    checks = {
        "HTTP 409": response.status_code == 409,
        "mensaje del límite": "5 enlaces" in detail,
        "listado vacío": list_tasks() == [],
    }
    obtained = "HTTP 409 con el detalle del límite; no se creó ninguna tarea"
    return make_result(
        "CP-ENL-03",
        checks,
        obtained,
        "Valor límite superior inválido de enlaces.",
        body,
    )


def cp_enl_04() -> dict:
    reset_server_db()
    duplicated = [
        {"url": "https://ejemplo.com/repetido"},
        {"url": "https://ejemplo.com/repetido"},
    ]
    response, body = post({"title": "Enlaces duplicados", "links": duplicated})
    detail = error_detail(body)
    checks = {
        "HTTP 409": response.status_code == 409,
        "mensaje de duplicado": "ya está agregado" in detail,
        "listado vacío": list_tasks() == [],
    }
    obtained = "HTTP 409 con el detalle del enlace duplicado; no se creó ninguna tarea"
    return make_result(
        "CP-ENL-04",
        checks,
        obtained,
        "Clase inválida: enlaces repetidos en la misma tarea.",
        body,
    )


# --- Historial de actividad (CP-HIS-01 y CP-HIS-02) ------------------------


def cp_his_01() -> dict:
    reset_server_db()
    task = create_task("Historial de la tarea")
    created = only_task(task["id"])
    created_actions = [entry.get("action") for entry in created.get("activity", [])]
    move(task["id"], {"status": "En curso"})
    updated = only_task(task["id"])
    updated_actions = [entry.get("action") for entry in updated.get("activity", [])]
    checks = {
        "creación registrada": "Tarea creada" in created_actions,
        "acción posterior registrada": "Movida a En curso" in updated_actions,
        "historial crece": len(updated_actions) > len(created_actions),
    }
    obtained = (
        'La creación dejó "Tarea creada" y el movimiento agregó '
        '"Movida a En curso"'
    )
    return make_result(
        "CP-HIS-01", checks, obtained, "Registro del historial de la tarea.", updated
    )


def cp_his_02() -> dict:
    reset_server_db()
    subtasks = [f"Paso {index:02d}" for index in range(1, 21)]
    response, body = post({"title": "Historial extenso", "subtasks": subtasks})
    activity = body.get("activity") or []
    actions = [entry.get("action") for entry in activity]
    ids = [entry.get("id") for entry in activity]
    checks = {
        "HTTP 201": response.status_code == 201,
        "máximo 20 entradas": len(activity) == 20,
        "más nueva primero": ids == sorted(ids, reverse=True),
        "la más nueva es el último paso": actions[0] == "Subtarea agregada: Paso 20",
        "la creación queda fuera": "Tarea creada" not in actions,
    }
    obtained = (
        "El historial devolvió 20 entradas como máximo, con la más reciente "
        "primero"
    )
    return make_result(
        "CP-HIS-02",
        checks,
        obtained,
        "Valor límite de cantidad del historial y orden descendente.",
        {"total": len(activity), "primera": actions[0] if actions else None},
    )


# --- Búsqueda y filtros (CP-FIL-01 a CP-FIL-03) ----------------------------


def cp_fil_01() -> dict:
    reset_server_db()
    high = post({"title": "Prioridad alta", "priority": "Alta"})[1]
    post({"title": "Prioridad baja", "priority": "Baja"})
    post({"title": "Prioridad media", "priority": "Media"})
    response = api("GET", "/api/tasks?priority=Alta")
    filtered = response.json()
    checks = {
        "filtro HTTP 200": response.status_code == 200,
        "solo la de prioridad Alta": [item["id"] for item in filtered] == [high["id"]],
        "sin filtro devuelve tres": len(list_tasks()) == 3,
    }
    obtained = "El filtro priority devolvió solo la tarea de prioridad Alta"
    return make_result(
        "CP-FIL-01", checks, obtained, "Filtro por prioridad.", {"filtered": filtered}
    )


def cp_fil_02() -> dict:
    reset_server_db()
    tagged = post({"title": "Tarea etiquetada", "tags": ["backend"]})[1]
    post({"title": "Tarea sin etiqueta"})
    response = api("GET", "/api/tasks?tag=backend")
    filtered = response.json()
    checks = {
        "filtro HTTP 200": response.status_code == 200,
        "solo la etiquetada": [item["id"] for item in filtered] == [tagged["id"]],
        "sin filtro devuelve dos": len(list_tasks()) == 2,
    }
    obtained = "El filtro tag devolvió solo la tarea con la etiqueta indicada"
    return make_result(
        "CP-FIL-02", checks, obtained, "Filtro por etiqueta.", {"filtered": filtered}
    )


def cp_fil_03() -> dict:
    reset_server_db()
    by_title = post({"title": "Informe mensual", "description": "Sin coincidencias"})[1]
    by_description = post(
        {"title": "Otra tarea", "description": "Revisar el INFORME final"}
    )[1]
    post({"title": "Tarea ajena", "description": "Sin relación"})
    response = api("GET", "/api/tasks?q=informe")
    filtered = response.json()
    found = sorted(item["id"] for item in filtered)
    checks = {
        "filtro HTTP 200": response.status_code == 200,
        "coincide por título y descripción": found
        == sorted([by_title["id"], by_description["id"]]),
        "sin distinguir mayúsculas": by_description["id"] in found,
        "excluye la ajena": len(filtered) == 2,
    }
    obtained = (
        "La búsqueda encontró coincidencias en el título y en la descripción, "
        "sin distinguir mayúsculas"
    )
    return make_result(
        "CP-FIL-03",
        checks,
        obtained,
        "Búsqueda por texto en título y descripción.",
        {"filtered": filtered},
    )


# --- Orden (CP-ORD-01 y CP-ORD-02) -----------------------------------------


def cp_ord_01() -> dict:
    reset_server_db()
    post({"title": "Baja", "priority": "Baja"})
    post({"title": "Alta", "priority": "Alta"})
    post({"title": "Media", "priority": "Media"})
    response = api("GET", "/api/tasks?sort=priority")
    ordered = response.json()
    order = [item["title"] for item in ordered]
    checks = {
        "HTTP 200": response.status_code == 200,
        "orden Alta, Media, Baja": order == ["Alta", "Media", "Baja"],
        "devuelve las tres": len(ordered) == 3,
    }
    obtained = "sort=priority ordenó las tareas como Alta, Media y Baja"
    return make_result(
        "CP-ORD-01",
        checks,
        obtained,
        "Orden por prioridad dentro del mismo estado.",
        {"order": order},
    )


def cp_ord_02() -> dict:
    reset_server_db()
    response = api("GET", "/api/tasks?sort=invalido")
    body = json_body(response)
    checks = {
        "HTTP 422": response.status_code == 422,
        "error de validación": isinstance(body, dict) and "detail" in body,
    }
    obtained = "HTTP 422 por valor de sort fuera de los permitidos"
    return make_result(
        "CP-ORD-02", checks, obtained, "Clase inválida del parámetro de orden.", body
    )


# --- Alta enriquecida (CP-ALT-01 y CP-ALT-02) ------------------------------


def cp_alt_01() -> dict:
    reset_server_db()
    payload = {
        "title": "Alta enriquecida",
        "priority": "Alta",
        "assignee": "Marta",
        "subtasks": ["Analizar", "Diseñar"],
        "tags": ["frontend", "backend"],
        "links": [{"url": "https://ejemplo.com/spec", "label": "Especificación"}],
    }
    response, body = post(payload)
    checks = {
        "HTTP 201": response.status_code == 201,
        "prioridad Alta": body.get("priority") == "Alta",
        "responsable Marta": body.get("assignee") == "Marta",
        "subtask_total 2": body.get("subtask_total") == 2,
        "dos subtareas": [item.get("title") for item in body.get("subtasks") or []]
        == ["Analizar", "Diseñar"],
        "dos etiquetas": sorted(body.get("tags") or []) == ["backend", "frontend"],
        "un enlace": len(body.get("links") or []) == 1,
    }
    obtained = (
        "HTTP 201; prioridad, responsable, 2 subtareas, 2 etiquetas y 1 enlace "
        "persistidos en un solo POST"
    )
    return make_result(
        "CP-ALT-01",
        checks,
        obtained,
        "Alta enriquecida en una sola petición.",
        body,
    )


def cp_alt_02() -> dict:
    reset_server_db()
    subtasks = [f"Paso {index}" for index in range(1, 22)]
    response, body = post({"title": "Demasiadas subtareas", "subtasks": subtasks})
    detail = error_detail(body)
    checks = {
        "HTTP 409": response.status_code == 409,
        "mensaje del límite": "20 subtareas" in detail,
        "listado vacío": list_tasks() == [],
    }
    obtained = "HTTP 409 con el detalle del límite; no se creó ninguna tarea"
    return make_result(
        "CP-ALT-02",
        checks,
        obtained,
        "Valor límite superior inválido de subtareas.",
        body,
    )


CASES = [
    cp_cre_01,
    cp_cre_02,
    cp_cre_03,
    cp_cre_04,
    cp_cre_05,
    cp_cre_06,
    cp_cre_07,
    cp_cre_08,
    cp_cre_09,
    cp_mov_01,
    cp_mov_02,
    cp_mov_03,
    cp_mov_04,
    cp_mov_05,
    cp_edi_01,
    cp_edi_02,
    cp_edi_03,
    cp_sub_01,
    cp_sub_02,
    cp_sub_03,
    cp_sub_04,
    cp_blo_01,
    cp_blo_02,
    cp_blo_03,
    cp_blo_04,
    cp_fec_01,
    cp_fec_02,
    cp_adj_01,
    cp_adj_02,
    cp_adj_03,
    cp_adj_04,
    cp_adj_05,
    cp_adj_06,
    cp_eli_01,
    cp_eli_02,
    cp_res_01,
    cp_res_02,
    cp_lis_01,
    cp_pri_01,
    cp_pri_02,
    cp_pri_03,
    cp_pri_04,
    cp_asg_01,
    cp_asg_02,
    cp_asg_03,
    cp_tag_01,
    cp_tag_02,
    cp_tag_03,
    cp_tag_04,
    cp_enl_01,
    cp_enl_02,
    cp_enl_03,
    cp_enl_04,
    cp_his_01,
    cp_his_02,
    cp_fil_01,
    cp_fil_02,
    cp_fil_03,
    cp_ord_01,
    cp_ord_02,
    cp_alt_01,
    cp_alt_02,
]


def main() -> int:
    ensure_server()
    results = []
    for case in CASES:
        result = case()
        results.append(result)
        state = "APROBADO" if result["passed"] else "FALLIDO"
        print(f"{result['id']}: {state} | {result['resultado_obtenido']}")
    save_json("resultados_api.json", results)
    failed = [item["id"] for item in results if not item["passed"]]
    print(f"\nAPI: {len(results) - len(failed)}/{len(results)} aprobados")
    if failed:
        print(f"Fallidos: {', '.join(failed)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
