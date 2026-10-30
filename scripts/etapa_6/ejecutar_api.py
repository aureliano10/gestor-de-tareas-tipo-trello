from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    api,
    create_task,
    ensure_server,
    make_result,
    reset_server_db,
    save_json,
    short,
)


def post_title(title: str):
    response = api("POST", "/api/tasks", {"title": title})
    try:
        body = response.json()
    except Exception:  # noqa: BLE001
        body = response.text
    return response, body


def list_tasks():
    response = api("GET", "/api/tasks")
    return response, response.json()


def creation_case(case_id: str, title: str, expected_status: int) -> dict:
    reset_server_db()
    response, body = post_title(title)
    _, tasks = list_tasks()
    expected_title = title.strip()
    if expected_status == 201:
        checks = {
            "HTTP 201": response.status_code == 201,
            "estado Pendiente": isinstance(body, dict)
            and body.get("status") == "Pendiente",
            "título almacenado": isinstance(body, dict)
            and body.get("title") == expected_title,
            "id entero": isinstance(body, dict) and isinstance(body.get("id"), int),
            "aparece en el listado": isinstance(body, dict)
            and any(item.get("id") == body.get("id") for item in tasks),
        }
        obtained = (
            f"HTTP {response.status_code}; respuesta={short(body)}; "
            f"listado={short(tasks)}"
        )
        observations = (
            f"Alta con título {title!r}; se esperaba HTTP 201 y persistencia."
        )
    else:
        checks = {
            "HTTP 422": response.status_code == 422,
            "listado vacío": isinstance(tasks, list) and len(tasks) == 0,
            "no se creó la tarea": not isinstance(body, dict)
            or "id" not in body,
        }
        obtained = (
            f"HTTP {response.status_code}; respuesta={short(body)}; "
            f"listado={short(tasks)}"
        )
        observations = (
            f"Alta rechazada con título {title!r}; se esperaba HTTP 422 "
            "y ningún registro."
        )
    return make_result(case_id, checks, obtained, observations, body)


def cp_cre_01() -> dict:
    return creation_case("CP-CRE-01", "Preparar informe", 201)


def cp_cre_02() -> dict:
    return creation_case("CP-CRE-02", "A", 201)


def cp_cre_03() -> dict:
    return creation_case("CP-CRE-03", "a" * 100, 201)


def cp_cre_04() -> dict:
    return creation_case("CP-CRE-04", "a" * 101, 422)


def cp_cre_05() -> dict:
    return creation_case("CP-CRE-05", "", 422)


def cp_cre_06() -> dict:
    return creation_case("CP-CRE-06", "     ", 422)


def cp_cre_07() -> dict:
    title = "  Revisar pruebas  "
    reset_server_db()
    response, body = post_title(title)
    _, tasks = list_tasks()
    checks = {
        "HTTP 201": response.status_code == 201,
        "título recortado": isinstance(body, dict)
        and body.get("title") == "Revisar pruebas",
        "estado Pendiente": isinstance(body, dict)
        and body.get("status") == "Pendiente",
        "persistencia recortada": any(
            item.get("title") == "Revisar pruebas" for item in tasks
        ),
    }
    obtained = (
        f"HTTP {response.status_code}; respuesta={short(body)}; "
        f"listado={short(tasks)}"
    )
    return make_result(
        "CP-CRE-07",
        checks,
        obtained,
        "Alta con espacios externos; se esperaba recorte y persistencia.",
        body,
    )


def cp_cre_08() -> dict:
    title = "Revisión de señalización #1 – ñandú"
    reset_server_db()
    response, body = post_title(title)
    _, tasks = list_tasks()
    checks = {
        "HTTP 201": response.status_code == 201,
        "caracteres especiales preservados": isinstance(body, dict)
        and body.get("title") == title,
        "estado Pendiente": isinstance(body, dict)
        and body.get("status") == "Pendiente",
        "persistencia exacta": any(item.get("title") == title for item in tasks),
    }
    obtained = (
        f"HTTP {response.status_code}; respuesta={short(body)}; "
        f"listado={short(tasks)}"
    )
    return make_result(
        "CP-CRE-08",
        checks,
        obtained,
        "Alta con acentos, eñe y símbolos; se esperaba conservación exacta.",
        body,
    )


def cp_mov_01() -> dict:
    reset_server_db()
    task = create_task("Mover a Terminada")
    r1 = api("PATCH", f"/api/tasks/{task['id']}/status", {"status": "En curso"})
    b1 = r1.json()
    r2 = api("PATCH", f"/api/tasks/{task['id']}/status", {"status": "Terminada"})
    b2 = r2.json()
    _, tasks = list_tasks()
    stored = next((item for item in tasks if item["id"] == task["id"]), None)
    checks = {
        "En curso HTTP 200": r1.status_code == 200,
        "En curso aplicado": b1.get("status") == "En curso",
        "Terminada HTTP 200": r2.status_code == 200,
        "Terminada aplicada": b2.get("status") == "Terminada",
        "persistido Terminada": stored is not None
        and stored.get("status") == "Terminada",
    }
    obtained = (
        f"En curso: HTTP {r1.status_code} ({b1.get('status')}); "
        f"Terminada: HTTP {r2.status_code} ({b2.get('status')}); "
        f"persistido={stored.get('status') if stored else None}"
    )
    return make_result(
        "CP-MOV-01",
        checks,
        obtained,
        "Transición completa Pendiente → En curso → Terminada.",
        {"en_curso": b1, "terminada": b2, "persistido": stored},
    )


def cp_mov_02() -> dict:
    reset_server_db()
    task = create_task("Estado inválido")
    response = api(
        "PATCH", f"/api/tasks/{task['id']}/status", {"status": "Finalizada"}
    )
    try:
        body = response.json()
    except Exception:  # noqa: BLE001
        body = response.text
    _, tasks = list_tasks()
    stored = next((item for item in tasks if item["id"] == task["id"]), None)
    checks = {
        "HTTP 422": response.status_code == 422,
        "estado sin cambios": stored is not None
        and stored.get("status") == "Pendiente",
    }
    obtained = (
        f"HTTP {response.status_code}; respuesta={short(body)}; "
        f"persistido={stored.get('status') if stored else None}"
    )
    return make_result(
        "CP-MOV-02",
        checks,
        obtained,
        "Intento de estado no permitido; se esperaba rechazo y sin cambios.",
        body,
    )


def cp_mov_03() -> dict:
    reset_server_db()
    response = api(
        "PATCH", "/api/tasks/999999/status", {"status": "En curso"}
    )
    try:
        body = response.json()
    except Exception:  # noqa: BLE001
        body = response.text
    checks = {
        "HTTP 404": response.status_code == 404,
        "mensaje Tarea no encontrada": isinstance(body, dict)
        and body.get("detail") == "Tarea no encontrada",
    }
    obtained = f"HTTP {response.status_code}; respuesta={short(body)}"
    return make_result(
        "CP-MOV-03",
        checks,
        obtained,
        "Actualización sobre id inexistente; se esperaba HTTP 404.",
        body,
    )


def cp_mov_04() -> dict:
    reset_server_db()
    response = api("PATCH", "/api/tasks/abc/status", {"status": "En curso"})
    try:
        body = response.json()
    except Exception:  # noqa: BLE001
        body = response.text
    checks = {
        "HTTP 422": response.status_code == 422,
        "error de validación": isinstance(body, dict) and "detail" in body,
    }
    obtained = f"HTTP {response.status_code}; respuesta={short(body)}"
    return make_result(
        "CP-MOV-04",
        checks,
        obtained,
        "Identificador no numérico; se esperaba HTTP 422.",
        body,
    )


def cp_eli_01() -> dict:
    reset_server_db()
    task = create_task("Eliminar esta tarea")
    response = api("DELETE", f"/api/tasks/{task['id']}")
    body = response.text
    _, tasks = list_tasks()
    checks = {
        "HTTP 204": response.status_code == 204,
        "sin cuerpo": body == "",
        "tarea ausente del listado": all(
            item.get("id") != task["id"] for item in tasks
        ),
    }
    obtained = (
        f"HTTP {response.status_code}; cuerpo={body!r}; "
        f"listado={short(tasks)}"
    )
    return make_result(
        "CP-ELI-01",
        checks,
        obtained,
        "Eliminación de una tarea existente; se esperaba HTTP 204.",
        {"id": task["id"], "listado": tasks},
    )


def cp_eli_02() -> dict:
    reset_server_db()
    response = api("DELETE", "/api/tasks/999999")
    try:
        body = response.json()
    except Exception:  # noqa: BLE001
        body = response.text
    checks = {
        "HTTP 404": response.status_code == 404,
        "mensaje Tarea no encontrada": isinstance(body, dict)
        and body.get("detail") == "Tarea no encontrada",
    }
    obtained = f"HTTP {response.status_code}; respuesta={short(body)}"
    return make_result(
        "CP-ELI-02",
        checks,
        obtained,
        "Eliminación sobre id inexistente; se esperaba HTTP 404.",
        body,
    )


def cp_lis_01() -> dict:
    reset_server_db()
    r_empty, empty = list_tasks()
    first = create_task("Primera tarea")
    second = create_task("Segunda tarea")
    r_list, tasks = list_tasks()
    ids = [item.get("id") for item in tasks]
    required_keys = {"id", "title", "status", "created_at"}
    checks = {
        "listado vacío HTTP 200": r_empty.status_code == 200 and empty == [],
        "listado HTTP 200": r_list.status_code == 200,
        "dos tareas": len(tasks) == 2,
        "ids ordenados": ids == sorted(ids),
        "orden de creación": ids == [first["id"], second["id"]],
        "campos completos": all(required_keys <= set(item) for item in tasks),
        "estados Pendiente": all(
            item.get("status") == "Pendiente" for item in tasks
        ),
    }
    obtained = (
        f"vacío HTTP {r_empty.status_code} {short(empty)}; "
        f"con datos HTTP {r_list.status_code} {short(tasks)}"
    )
    return make_result(
        "CP-LIS-01",
        checks,
        obtained,
        "Listado vacío y con dos tareas en orden de creación.",
        {"vacio": empty, "tareas": tasks},
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
    cp_mov_01,
    cp_mov_02,
    cp_mov_03,
    cp_mov_04,
    cp_eli_01,
    cp_eli_02,
    cp_lis_01,
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
