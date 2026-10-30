from __future__ import annotations

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
from playwright.sync_api import sync_playwright  # noqa: E402
from ui_helpers import (  # noqa: E402
    drag_task,
    open_page,
    reload_board,
    screenshot,
    task_in,
    track_requests,
)


def ui_01(page, _prepared) -> dict:
    title = "Tarea desde interfaz"
    page.fill("#task-title", title)
    page.click('.task-form button[type="submit"]')
    card = task_in(page, "Pendiente", title)
    card.wait_for(timeout=10000)
    visible = card.count() == 1
    input_value = page.input_value("#task-title")
    count = page.inner_text('.column[data-status="Pendiente"] .column__count')
    reload_board(page)
    persisted = task_in(page, "Pendiente", title).count() == 1
    checks = {
        "tarjeta en Pendiente": visible,
        "campo vacío tras alta": input_value == "",
        "contador Pendiente en 1": count.strip() == "1",
        "persiste tras recargar": persisted,
    }
    obtained = (
        f"Tarjeta visible={visible}; input={input_value!r}; "
        f"contador={count.strip()}; persistió={persisted}"
    )
    return make_result(
        "CP-UI-01",
        checks,
        obtained,
        "Alta desde el formulario y verificación tras recargar.",
    )


def ui_02(page, _prepared) -> dict:
    posts = track_requests(page, "POST", "/api/tasks")
    page.fill("#task-title", "     ")
    page.click('.task-form button[type="submit"]')
    page.wait_for_selector(".task-form__error", timeout=5000)
    error = page.inner_text(".task-form__error")
    page.wait_for_timeout(500)
    expected = "El título es obligatorio y no puede contener solo espacios."
    checks = {
        "mensaje de error correcto": error == expected,
        "sin tareas creadas": page.locator(".task").count() == 0,
        "sin petición POST": len(posts) == 0,
    }
    obtained = (
        f"error={error!r}; tarjetas={page.locator('.task').count()}; "
        f"POST={len(posts)}"
    )
    return make_result(
        "CP-UI-02",
        checks,
        obtained,
        "Intento de alta con espacios; se esperaba validación en cliente.",
    )


def prepare_single(title: str):
    def prepare():
        return create_task(title)

    return prepare


def ui_03(page, task) -> dict:
    title = task["title"]
    patches = track_requests(page, "PATCH", "/api/tasks/")
    drag_task(page, task["id"], "En curso")
    task_in(page, "En curso", title).wait_for(timeout=10000)
    page.wait_for_timeout(300)
    in_progress = task_in(page, "En curso", title).count() == 1
    pending = task_in(page, "Pendiente", title).count()
    patches_done = len(patches)
    reload_board(page)
    persisted = task_in(page, "En curso", title).count() == 1
    checks = {
        "tarjeta en En curso": in_progress,
        "tarjeta fuera de Pendiente": pending == 0,
        "PATCH emitido": patches_done >= 1,
        "persiste tras recargar": persisted,
    }
    obtained = (
        f"En curso={in_progress}; Pendiente={pending}; "
        f"PATCH={patches_done}; persistió={persisted}"
    )
    return make_result(
        "CP-UI-03",
        checks,
        obtained,
        "Arrastre de Pendiente a En curso y persistencia.",
    )


def ui_04(page, task) -> dict:
    title = task["title"]
    patches = track_requests(page, "PATCH", "/api/tasks/")
    drag_task(page, task["id"], "Pendiente")
    page.wait_for_timeout(500)
    checks = {
        "sin petición PATCH": len(patches) == 0,
        "tarjeta sigue en Pendiente": task_in(page, "Pendiente", title).count() == 1,
        "contador Pendiente en 1": page.inner_text(
            '.column[data-status="Pendiente"] .column__count'
        ).strip()
        == "1",
    }
    obtained = f"PATCH={len(patches)}; tarjeta en Pendiente=" + str(
        task_in(page, "Pendiente", title).count()
    )
    return make_result(
        "CP-UI-04",
        checks,
        obtained,
        "Arrastre dentro de la misma columna; no debía generar cambios.",
    )


def ui_05(page, task) -> dict:
    title = task["title"]
    deletes = track_requests(page, "DELETE", "/api/tasks/")
    card = task_in(page, "Pendiente", title)
    card.locator("button.task__delete").click()
    card.wait_for(state="detached", timeout=10000)
    page.wait_for_timeout(300)
    remaining = page.locator(".task").count()
    deletes_done = len(deletes)
    reload_board(page)
    persisted = page.locator(".task").count()
    checks = {
        "tarjeta eliminada": remaining == 0,
        "DELETE emitido": deletes_done >= 1,
        "sin tareas tras recargar": persisted == 0,
    }
    obtained = (
        f"tarjetas restantes={remaining}; DELETE={deletes_done}; "
        f"tras recarga={persisted}"
    )
    return make_result(
        "CP-UI-05",
        checks,
        obtained,
        "Eliminación desde la tarjeta y verificación tras recargar.",
    )


CASES = [
    ("CP-UI-01", ui_01, None),
    ("CP-UI-02", ui_02, None),
    ("CP-UI-03", ui_03, prepare_single("Mover desde interfaz")),
    ("CP-UI-04", ui_04, prepare_single("Mantener columna")),
    ("CP-UI-05", ui_05, prepare_single("Eliminar desde interfaz")),
]


def run_case(browser, case_id: str, fn, prepare) -> dict:
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
    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        try:
            for case_id, fn, prepare in CASES:
                result = run_case(browser, case_id, fn, prepare)
                results.append(result)
                state = "APROBADO" if result["passed"] else "FALLIDO"
                print(f"{case_id}: {state} | {result['resultado_obtenido']}")
        finally:
            browser.close()
    save_json("resultados_ui.json", results)
    failed = [item["id"] for item in results if not item["passed"]]
    print(f"\nUI: {len(results) - len(failed)}/{len(results)} aprobados")
    if failed:
        print(f"Fallidos: {', '.join(failed)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
