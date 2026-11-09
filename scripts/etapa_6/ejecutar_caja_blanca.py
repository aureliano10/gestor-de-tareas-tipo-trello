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
from ui_helpers import (  # noqa: E402
    FORM_DESCRIPTION,
    FORM_ERROR,
    FORM_MODAL,
    FORM_SUBMIT,
    FORM_TITLE,
    drag_task,
    drop_raw,
    launch_browser,
    open_page,
    open_task_form,
    request_bodies,
    screenshot,
    set_field_value,
    task_in,
    track_requests,
    wait_text,
    wait_titles,
)

from app import repository  # noqa: E402
from app.database import connection, init_db  # noqa: E402
from app.schemas import (  # noqa: E402
    EMPTY_TITLE_MESSAGE,
    TOO_LONG_TITLE_MESSAGE,
    clean_title,
)


def clean_wb_db() -> None:
    with connection() as conn:
        conn.execute("DELETE FROM attachments")
        conn.execute("DELETE FROM subtasks")
        conn.execute("DELETE FROM tasks")


def clean_title_outcome(value) -> tuple[str | None, str | None]:
    try:
        return clean_title(value), None
    except ValueError as exc:
        return None, str(exc)


def cb_01() -> dict:
    valid, valid_error = clean_title_outcome("  Tarea válida  ")
    empty, empty_error = clean_title_outcome("")
    spaces, spaces_error = clean_title_outcome("     ")
    long_value, long_error = clean_title_outcome("a" * 101)
    none_value, none_error = clean_title_outcome(None)

    checks = {
        "título válido recortado": valid == "Tarea válida" and valid_error is None,
        "vacío rechazado": empty is None and empty_error == EMPTY_TITLE_MESSAGE,
        "solo espacios rechazado": spaces is None
        and spaces_error == EMPTY_TITLE_MESSAGE,
        "más de 100 rechazado": long_value is None
        and long_error == TOO_LONG_TITLE_MESSAGE,
        "valor nulo rechazado": none_value is None
        and none_error == "El título es obligatorio",
    }
    obtained = (
        f"válido={valid!r}; vacío={empty_error!r}; espacios={spaces_error!r}; "
        f"101={long_error!r}; None={none_error!r}"
    )
    return make_result(
        "CP-CB-01",
        checks,
        obtained,
        "Decisiones del validador de título. La rama del valor nulo es "
        "defensiva: Pydantic rechaza el valor antes de ejecutarla.",
    )


def cb_02() -> dict:
    clean_wb_db()
    blocked = repository.create_task("Con subtarea pendiente")
    repository.create_subtask(blocked["id"], "Paso pendiente", done=False)

    missing = repository.move_task(999999, "En curso")
    try:
        repository.move_task(blocked["id"], "Terminada")
        pending_error = None
    except repository.PendingSubtasksError as exc:
        pending_error = exc

    ready = repository.create_task("Lista para finalizar")
    repository.create_subtask(ready["id"], "Paso hecho", done=True)
    finished = repository.move_task(ready["id"], "Terminada")

    checks = {
        "id inexistente devuelve None": missing is None,
        "finalización bloqueada lanza PendingSubtasksError": pending_error is not None
        and pending_error.pending == 1,
        "tarea bloqueada sigue en Pendiente": repository.get_task(blocked["id"])[
            "status"
        ]
        == "Pendiente",
        "finalización permitida devuelve Terminada": finished is not None
        and finished["status"] == "Terminada",
    }
    obtained = (
        f"inexistente={missing!r}; bloqueada={pending_error!r}; "
        f"estado bloqueado={repository.get_task(blocked['id'])['status']!r}; "
        f"finalizada={finished['status'] if finished else None!r}"
    )
    return make_result(
        "CP-CB-02",
        checks,
        obtained,
        "Tres decisiones de move_task: fila inexistente, finalización "
        "bloqueada por subtareas pendientes y finalización permitida.",
    )


def cb_03() -> dict:
    clean_wb_db()
    created = repository.create_task("Eliminar y restaurar")

    deleted = repository.delete_task(created["id"])
    after_delete = repository.list_tasks()
    second_delete = repository.delete_task(created["id"])
    missing_delete = repository.delete_task(999999)

    restored = repository.restore_task(created["id"])
    after_restore = repository.list_tasks()
    second_restore = repository.restore_task(created["id"])
    missing_restore = repository.restore_task(999999)

    checks = {
        "eliminación existente devuelve True": deleted is True,
        "la tarea sale del listado": after_delete == [],
        "segunda eliminación devuelve False": second_delete is False,
        "eliminación inexistente devuelve False": missing_delete is False,
        "restauración devuelve la tarea": restored is not None
        and restored["id"] == created["id"],
        "la tarea vuelve al listado": len(after_restore) == 1,
        "restauración de tarea activa devuelve None": second_restore is None,
        "restauración inexistente devuelve None": missing_restore is None,
    }
    obtained = (
        f"delete={deleted}; listado tras delete={len(after_delete)}; "
        f"segundo delete={second_delete}; delete inexistente={missing_delete}; "
        f"restore={'ok' if restored else None}; listado tras restore="
        f"{len(after_restore)}; segundo restore={second_restore!r}; "
        f"restore inexistente={missing_restore!r}"
    )
    return make_result(
        "CP-CB-03",
        checks,
        obtained,
        "Borrado lógico y sus dos resultados de restauración.",
    )


def cb_04() -> dict:
    clean_wb_db()
    created = repository.create_task("Tarea con adjuntos")

    totals = []
    for index in range(1, 4):
        task = repository.create_attachment(
            created["id"],
            f"archivo{index}.txt",
            f"stored{index}.txt",
            "text/plain",
            12,
        )
        totals.append(len(task["attachments"]))

    try:
        repository.create_attachment(
            created["id"], "archivo4.txt", "stored4.txt", "text/plain", 12
        )
        limit_error = None
    except repository.AttachmentLimitError as exc:
        limit_error = exc

    final_total = len(repository.get_task(created["id"])["attachments"])

    checks = {
        "tres altas válidas acumulan 1, 2 y 3": totals == [1, 2, 3],
        "cuarta alta lanza AttachmentLimitError": limit_error is not None
        and limit_error.limit == 3,
        "la tarea conserva 3 adjuntos": final_total == 3,
    }
    obtained = (
        f"acumulado={totals}; cuarta alta={limit_error!r}; "
        f"adjuntos finales={final_total}"
    )
    return make_result(
        "CP-CB-04",
        checks,
        obtained,
        "La decisión del límite de adjuntos cubre sus dos resultados.",
    )


def cb_05() -> dict:
    clean_wb_db()
    finished = repository.create_task("Tarea terminada")
    finished_sub = repository.create_subtask(finished["id"], "Paso único", done=True)
    subtask_id = finished_sub["subtasks"][0]["id"]
    repository.move_task(finished["id"], "Terminada")
    before_reopen = repository.get_task(finished["id"])["status"]

    reopened = repository.update_subtask(subtask_id, done=False)

    pending = repository.create_task("Tarea pendiente")
    pending_sub = repository.create_subtask(pending["id"], "Otro paso", done=False)
    pending_subtask_id = pending_sub["subtasks"][0]["id"]
    kept = repository.update_subtask(pending_subtask_id, done=True)

    checks = {
        "la tarea estaba Terminada": before_reopen == "Terminada",
        "desmarcar reabre la tarea a En curso": reopened is not None
        and reopened["status"] == "En curso",
        "la subtarea quedó sin completar": reopened is not None
        and reopened["subtask_done"] == 0,
        "marcar no cambia una tarea Pendiente": kept is not None
        and kept["status"] == "Pendiente",
    }
    obtained = (
        f"estado previo={before_reopen!r}; tras desmarcar="
        f"{reopened['status'] if reopened else None!r}; "
        f"pendientes={reopened['subtask_done'] if reopened else None}; "
        f"tras marcar={kept['status'] if kept else None!r}"
    )
    return make_result(
        "CP-CB-05",
        checks,
        obtained,
        "Condición compuesta de reapertura: `not done and status == Terminada`.",
    )


def cb_06(page, _prepared) -> dict:
    posts = track_requests(page, "POST", "/api/tasks")
    empty_expected = "El título es obligatorio y no puede contener solo espacios."
    long_title_expected = "El título no puede superar los 100 caracteres."
    long_description_expected = "La descripción no puede superar los 500 caracteres."

    open_task_form(page)
    page.click(FORM_SUBMIT)
    empty_message = wait_text(page.locator(FORM_ERROR), empty_expected, timeout=5.0)

    page.fill(FORM_TITLE, "     ")
    page.click(FORM_SUBMIT)
    spaces_message = wait_text(page.locator(FORM_ERROR), empty_expected, timeout=5.0)

    set_field_value(page, FORM_TITLE, "a" * 101, max_length=101)
    loaded_length = len(page.input_value(FORM_TITLE))
    page.click(FORM_SUBMIT)
    long_title_message = wait_text(
        page.locator(FORM_ERROR), long_title_expected, timeout=5.0
    )

    page.fill(FORM_TITLE, "Tarea con descripción larga")
    set_field_value(page, FORM_DESCRIPTION, "d" * 501, max_length=501)
    page.click(FORM_SUBMIT)
    long_description_message = wait_text(
        page.locator(FORM_ERROR), long_description_expected, timeout=5.0
    )
    page.fill(FORM_DESCRIPTION, "")
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
    page.fill(FORM_TITLE, "Tarea con error simulado")
    page.click(FORM_SUBMIT)
    api_error = wait_text(
        page.locator(FORM_ERROR), "Error simulado de red", timeout=10000
    )
    cards_after_error = page.locator(".task").count()
    page.unroute("**/api/tasks", handler)

    page.fill(FORM_TITLE, "Tarea válida")
    page.click(FORM_SUBMIT)
    task_in(page, "Pendiente", "Tarea válida").wait_for(timeout=10000)
    valid_created = task_in(page, "Pendiente", "Tarea válida").count() == 1
    form_closed_after_valid = page.locator(FORM_MODAL).count() == 0
    total_posts = len(posts)

    checks = {
        "título vacío muestra el error": empty_message == empty_expected,
        "título de solo espacios muestra el error": spaces_message == empty_expected,
        "101 caracteres cargados en el campo": loaded_length == 101,
        "título de 101 muestra el error de longitud": long_title_message
        == long_title_expected,
        "descripción de 501 muestra el error de descripción": long_description_message
        == long_description_expected,
        "las ramas inválidas no emiten POST": posts_after_invalid == 0,
        "el error de la API se muestra": api_error == "Error simulado de red",
        "sin tarjeta tras el error de la API": cards_after_error == 0,
        "el alta válida crea la tarjeta": valid_created,
        "el modal se cierra tras el alta": form_closed_after_valid,
        "se emitieron dos POST: el fallido y el válido": total_posts == 2,
    }
    obtained = (
        f"vacío={empty_message!r}; espacios={spaces_message!r}; "
        f"len(101)={loaded_length}; título largo={long_title_message!r}; "
        f"descripción larga={long_description_message!r}; "
        f"POST inválidos={posts_after_invalid}; error API={api_error!r}; "
        f"tarjetas tras error={cards_after_error}; alta válida={valid_created}; "
        f"modal cerrado tras alta={form_closed_after_valid}; POST totales={total_posts}"
    )
    return make_result(
        "CP-CB-06",
        checks,
        obtained,
        "Ramas de validateTaskInput y handleSubmit ejercitadas sobre el "
        "formulario real.",
    )


def prepare_two_tasks() -> dict:
    return {"alfa": create_task("Alfa"), "beta": create_task("Beta")}


def cb_07(page, prepared) -> dict:
    page.wait_for_function(
        '() => document.querySelectorAll(\'.column[data-status="Pendiente"] '
        ".task').length === 2",
        timeout=10000,
    )
    patches = track_requests(page, "PATCH", "/api/tasks/")
    initial_order = wait_titles(page, "Pendiente", ["Alfa", "Beta"], timeout=5.0)

    drag_task(page, prepared["beta"]["id"], "Pendiente", client_y=0)
    reordered = wait_titles(page, "Pendiente", ["Beta", "Alfa"], timeout=10.0)
    same_column_bodies = request_bodies(patches)

    drag_task(page, prepared["alfa"]["id"], "En curso", client_y=0)
    task_in(page, "En curso", "Alfa").wait_for(timeout=10000)
    moved_bodies = request_bodies(patches)
    in_progress = task_in(page, "En curso", "Alfa").count() == 1

    drop_raw(page, "abc", "Terminada")
    drop_raw(page, "0", "Terminada")
    page.wait_for_timeout(500)
    total_patches = len(patches)
    finished_cards = page.locator('.column[data-status="Terminada"] .task').count()

    checks = {
        "orden inicial Alfa, Beta": initial_order == ["Alfa", "Beta"],
        "reordenar emite un PATCH": len(same_column_bodies) == 1,
        "el PATCH de reorden usa posición 0": same_column_bodies
        == [{"status": "Pendiente", "position": 0}],
        "el orden visible queda Beta, Alfa": reordered == ["Beta", "Alfa"],
        "mover de columna agrega un segundo PATCH": len(moved_bodies) == 2,
        "el PATCH de movimiento usa el estado destino": moved_bodies[1]
        == {"status": "En curso", "position": 0},
        "la tarjeta quedó en En curso": in_progress,
        "los identificadores inválidos no emiten PATCH": total_patches == 2,
        "nada llegó a Terminada": finished_cards == 0,
    }
    obtained = (
        f"orden inicial={initial_order}; PATCH reorden={same_column_bodies}; "
        f"orden final={reordered}; PATCH movimiento={moved_bodies}; "
        f"En curso={in_progress}; PATCH totales={total_patches}; "
        f"tarjetas en Terminada={finished_cards}"
    )
    return make_result(
        "CP-CB-07",
        checks,
        obtained,
        "Decisiones de handleDrop y valor devuelto por dropIndex: misma "
        "columna, columna distinta e identificadores inválidos.",
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
    backend_results = [cb_01(), cb_02(), cb_03(), cb_04(), cb_05()]

    frontend_results = []
    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        try:
            frontend_results.append(run_frontend_case(browser, "CP-CB-06", cb_06))
            frontend_results.append(
                run_frontend_case(browser, "CP-CB-07", cb_07, prepare=prepare_two_tasks)
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
