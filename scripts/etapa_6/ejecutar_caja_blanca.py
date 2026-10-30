from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    create_task,
    ensure_server,
    make_result,
    reset_server_db,
    save_json,
)

ROOT = Path(__file__).resolve().parents[2]
WB_DB_PATH = Path("/tmp/kanban_etapa6_wb.db")
os.environ["KANBAN_DB_PATH"] = str(WB_DB_PATH)
sys.path.insert(0, str(ROOT / "backend"))

from playwright.sync_api import sync_playwright  # noqa: E402
from pydantic import ValidationError  # noqa: E402
from ui_helpers import (  # noqa: E402
    drag_task,
    drop_raw,
    open_page,
    screenshot,
    set_input_value,
    task_in,
    track_requests,
)

from app import repository  # noqa: E402
from app.database import connection, init_db  # noqa: E402
from app.schemas import TaskCreate  # noqa: E402


def clean_wb_db() -> None:
    with connection() as conn:
        conn.execute("DELETE FROM tasks")


def validation_message(value) -> str | None:
    try:
        TaskCreate(title=value)
    except ValidationError as exc:
        return exc.errors()[0]["msg"]
    return None


def cb_01() -> dict:
    valid = TaskCreate(title="  Tarea válida  ")
    empty_message = validation_message("")
    spaces_message = validation_message("     ")
    long_message = validation_message("a" * 101)
    none_message = validation_message(None)
    checks = {
        "título válido recortado": valid.title == "Tarea válida",
        "vacío rechazado": empty_message is not None
        and "vacío" in empty_message,
        "solo espacios rechazado": spaces_message is not None
        and "vacío" in spaces_message,
        "más de 100 rechazado": long_message is not None
        and "100" in long_message,
        "rama None no alcanzable vía Pydantic": none_message is not None,
    }
    obtained = (
        f"válido={valid.title!r}; vacío={empty_message!r}; "
        f"espacios={spaces_message!r}; 101={long_message!r}; "
        f"None={none_message!r}"
    )
    return make_result(
        "CP-CB-01",
        checks,
        obtained,
        "Ramas del validador de título. La rama value is None no es "
        "alcanzable a través de Pydantic porque el tipo str se valida antes; "
        "se documenta como cobertura no alcanzable.",
    )


def cb_02() -> dict:
    clean_wb_db()
    created = repository.create_task("Actualizar estado")
    updated = repository.update_task_status(created["id"], "En curso")
    missing = repository.update_task_status(999999, "Terminada")
    checks = {
        "alta en Pendiente": created["status"] == "Pendiente",
        "actualización existente": updated is not None
        and updated["status"] == "En curso",
        "actualización inexistente devuelve None": missing is None,
    }
    obtained = (
        f"creada={created['status']}; actualizada="
        f"{updated['status'] if updated else None}; inexistente={missing!r}"
    )
    return make_result(
        "CP-CB-02",
        checks,
        obtained,
        "Ramas de update_task_status: fila actualizada y fila inexistente.",
        {"created": created, "updated": updated},
    )


def cb_03() -> dict:
    clean_wb_db()
    created = repository.create_task("Eliminar tarea")
    first = repository.delete_task(created["id"])
    second = repository.delete_task(created["id"])
    missing = repository.delete_task(999999)
    remaining = repository.list_tasks()
    checks = {
        "primera eliminación devuelve True": first is True,
        "segunda eliminación devuelve False": second is False,
        "id inexistente devuelve False": missing is False,
        "listado queda vacío": remaining == [],
    }
    obtained = (
        f"primera={first}; segunda={second}; inexistente={missing}; "
        f"restantes={len(remaining)}"
    )
    return make_result(
        "CP-CB-03",
        checks,
        obtained,
        "Ramas de delete_task: fila eliminada y fila inexistente.",
        {"created": created, "remaining": remaining},
    )


def cb_04(page, _prepared) -> dict:
    posts = track_requests(page, "POST", "/api/tasks")
    empty_expected = "El título es obligatorio y no puede contener solo espacios."
    page.click('.task-form button[type="submit"]')
    page.wait_for_selector(".task-form__error", timeout=5000)
    empty_message = page.inner_text(".task-form__error")

    page.fill("#task-title", "     ")
    page.click('.task-form button[type="submit"]')
    page.wait_for_timeout(150)
    spaces_message = page.inner_text(".task-form__error")

    set_input_value(page, "a" * 101)
    loaded_length = len(page.input_value("#task-title"))
    page.click('.task-form button[type="submit"]')
    page.wait_for_timeout(150)
    long_message = page.inner_text(".task-form__error")
    page.wait_for_timeout(300)
    posts_after_invalid = len(posts)

    def handler(route):
        if route.request.method == "POST":
            route.fulfill(
                status=500,
                content_type="application/json",
                body='{"detail":"Error simulado de red"}',
            )
        else:
            route.continue_()

    page.route("**/api/tasks", handler)
    page.fill("#task-title", "Tarea con error simulado")
    page.click('.task-form button[type="submit"]')
    page.wait_for_function(
        "() => document.querySelector('.task-form__error')?.textContent "
        "=== 'Error simulado de red'",
        timeout=5000,
    )
    api_error = page.inner_text(".task-form__error")
    cards_after_error = page.locator(".task").count()
    page.unroute("**/api/tasks", handler)

    page.fill("#task-title", "Tarea válida UI")
    page.click('.task-form button[type="submit"]')
    task_in(page, "Pendiente", "Tarea válida UI").wait_for(timeout=10000)
    valid_created = task_in(page, "Pendiente", "Tarea válida UI").count() == 1
    input_after_valid = page.input_value("#task-title")
    total_posts = len(posts)

    long_expected = "El título no puede superar los 100 caracteres."
    checks = {
        "vacío muestra error": empty_message == empty_expected,
        "solo espacios muestra error": spaces_message == empty_expected,
        "101 caracteres cargados": loaded_length == 101,
        "más de 100 muestra error": long_message == long_expected,
        "sin POST en ramas inválidas": posts_after_invalid == 0,
        "error de API visible": api_error == "Error simulado de red",
        "sin tarjeta tras error de API": cards_after_error == 0,
        "alta válida crea tarjeta": valid_created,
        "campo vacío tras alta válida": input_after_valid == "",
        "dos POST: fallido y válido": total_posts == 2,
    }
    obtained = (
        f"vacío={empty_message!r}; espacios={spaces_message!r}; "
        f"len101={loaded_length}; largo={long_message!r}; "
        f"POST inválidos={posts_after_invalid}; error API={api_error!r}; "
        f"tarjetas tras error={cards_after_error}; alta válida={valid_created}; "
        f"input={input_after_valid!r}; POST totales={total_posts}"
    )
    return make_result(
        "CP-CB-04",
        checks,
        obtained,
        "Ramas de handleSubmit ejecutadas sobre la interfaz real.",
    )


def cb_05(page, task) -> dict:
    title = task["title"]
    patches = track_requests(page, "PATCH", "/api/tasks/")
    drag_task(page, task["id"], "Pendiente")
    page.wait_for_timeout(400)
    same_column = len(patches)

    drag_task(page, task["id"], "En curso")
    task_in(page, "En curso", title).wait_for(timeout=10000)
    page.wait_for_timeout(300)
    valid_move = len(patches)

    drop_raw(page, "abc", "Terminada")
    drop_raw(page, "0", "Terminada")
    page.wait_for_timeout(400)
    after_invalid = len(patches)

    checks = {
        "sin PATCH en misma columna": same_column == 0,
        "un PATCH al mover de columna": valid_move == 1,
        "sin PATCH con id inválido": after_invalid == 1,
        "tarjeta permanece en En curso": task_in(
            page, "En curso", title
        ).count()
        == 1,
        "tarjeta no llegó a Terminada": task_in(
            page, "Terminada", title
        ).count()
        == 0,
    }
    obtained = (
        f"PATCH misma columna={same_column}; PATCH movimiento={valid_move}; "
        f"PATCH tras ids inválidos={after_invalid}; "
        f"En curso={task_in(page, 'En curso', title).count()}; "
        f"Terminada={task_in(page, 'Terminada', title).count()}"
    )
    return make_result(
        "CP-CB-05",
        checks,
        obtained,
        "Ramas de handleDrop: misma columna, movimiento válido e ids inválidos.",
    )


def run_frontend_case(browser, case_id: str, fn, prepare=None) -> dict:
    reset_server_db()
    prepared = prepare() if prepare else None
    context = None
    page = None
    try:
        context, page = open_page(browser)
        result = fn(page, prepared)
        screenshot(page, case_id)
    except Exception as exc:  # noqa: BLE001
        result = make_result(
            case_id,
            {"ejecución sin excepciones": False},
            f"Excepción: {exc}",
            "La ejecución del caso se interrumpió.",
        )
        if page is not None:
            try:
                screenshot(page, case_id)
            except Exception:  # noqa: BLE001
                pass
    finally:
        if context is not None:
            context.close()
    return result


def main() -> int:
    ensure_server()
    WB_DB_PATH.unlink(missing_ok=True)
    init_db()
    backend_results = [cb_01(), cb_02(), cb_03()]

    frontend_results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        try:
            frontend_results.append(
                run_frontend_case(browser, "CP-CB-04", cb_04)
            )
            frontend_results.append(
                run_frontend_case(
                    browser,
                    "CP-CB-05",
                    cb_05,
                    prepare=lambda: create_task("Blanco mover"),
                )
            )
        finally:
            browser.close()

    results = backend_results + frontend_results
    for result in results:
        state = "APROBADO" if result["passed"] else "FALLIDO"
        print(f"{result['id']}: {state} | {result['resultado_obtenido']}")
    save_json("resultados_caja_blanca.json", results)
    failed = [item["id"] for item in results if not item["passed"]]
    print(f"\nCaja blanca: {len(results) - len(failed)}/{len(results)} aprobados")
    if failed:
        print(f"Fallidos: {', '.join(failed)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
