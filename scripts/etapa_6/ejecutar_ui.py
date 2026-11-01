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
    FORM_ERROR,
    FORM_SUBMIT,
    FORM_TITLE,
    attachments_panel,
    card,
    checklist_panel,
    column_count,
    column_titles,
    drag_task,
    fetch_download,
    open_detail,
    open_page,
    reload_board,
    request_bodies,
    screenshot,
    task_in,
    track_requests,
    wait_text,
    wait_titles,
)


def ui_01(page, _prepared) -> dict:
    title = "Tarea desde interfaz"
    page.fill(FORM_TITLE, title)
    page.click(FORM_SUBMIT)
    task_in(page, "Pendiente", title).wait_for(timeout=10000)

    visible = task_in(page, "Pendiente", title).count() == 1
    input_value = page.input_value(FORM_TITLE)
    summary = page.inner_text('[data-testid="task-count"]').strip()
    pending_count = column_count(page, "Pendiente")

    reload_board(page)
    persisted = task_in(page, "Pendiente", title).count() == 1

    checks = {
        "tarjeta visible en Pendiente": visible,
        "el campo de título queda vacío": input_value == "",
        "el resumen general muestra 1 tarea": summary == "1 tarea",
        "el contador de Pendiente muestra 1": pending_count == "1",
        "la tarea persiste tras recargar": persisted,
    }
    obtained = (
        f"tarjeta visible={visible}; input={input_value!r}; resumen={summary!r}; "
        f"contador Pendiente={pending_count!r}; persistió={persisted}"
    )
    return make_result(
        "CP-UI-01",
        checks,
        obtained,
        "Alta desde el formulario con verificación visual y persistencia.",
    )


def ui_02(page, _prepared) -> dict:
    posts = track_requests(page, "POST", "/api/tasks")
    expected = "El título es obligatorio y no puede contener solo espacios."

    page.fill(FORM_TITLE, "     ")
    page.click(FORM_SUBMIT)
    error = wait_text(page.locator(FORM_ERROR), expected, timeout=5.0)

    page.wait_for_timeout(300)
    checks = {
        "mensaje de error correcto": error == expected,
        "no se creó ninguna tarjeta": page.locator(".task").count() == 0,
        "no se emitió ninguna petición POST": len(posts) == 0,
    }
    obtained = (
        f"error={error!r}; tarjetas={page.locator('.task').count()}; POST={len(posts)}"
    )
    return make_result(
        "CP-UI-02",
        checks,
        obtained,
        "Clase inválida y valor límite inferior sobre la interfaz.",
    )


def prepare_single(title: str, description: str = ""):
    def prepare():
        return create_task(title, description)

    return prepare


def prepare_pair():
    return {"primera": create_task("Primera"), "segunda": create_task("Segunda")}


def ui_03(page, task) -> dict:
    title = task["title"]
    patches = track_requests(page, "PATCH", "/api/tasks/")

    drag_task(page, task["id"], "En curso")
    task_in(page, "En curso", title).wait_for(timeout=10000)
    page.wait_for_timeout(300)

    in_progress = task_in(page, "En curso", title).count() == 1
    pending_cards = page.locator('.column[data-status="Pendiente"] .task').count()
    patches_done = len(patches)
    pending_count = column_count(page, "Pendiente")
    progress_count = column_count(page, "En curso")

    reload_board(page)
    persisted = task_in(page, "En curso", title).count() == 1

    checks = {
        "la tarjeta aparece en En curso": in_progress,
        "la tarjeta sale de Pendiente": pending_cards == 0,
        "el contador de Pendiente queda en 0": pending_count == "0",
        "el contador de En curso queda en 1": progress_count == "1",
        "se emitió un PATCH": patches_done == 1,
        "el movimiento persiste tras recargar": persisted,
    }
    obtained = (
        f"En curso={in_progress}; tarjetas en Pendiente={pending_cards}; "
        f"contador Pendiente={pending_count!r}; contador En curso="
        f"{progress_count!r}; PATCH={patches_done}; persistió={persisted}"
    )
    return make_result(
        "CP-UI-03",
        checks,
        obtained,
        "Arrastre entre columnas con actualización de contadores y persistencia.",
    )


def ui_04(page, prepared) -> dict:
    second = prepared["segunda"]
    page.wait_for_function(
        '() => document.querySelectorAll(\'.column[data-status="Pendiente"] '
        ".task').length === 2",
        timeout=10000,
    )
    initial_order = wait_titles(page, "Pendiente", ["Primera", "Segunda"], timeout=5.0)
    patches = track_requests(page, "PATCH", "/api/tasks/")

    drag_task(page, second["id"], "Pendiente", client_y=0)
    final_order = wait_titles(page, "Pendiente", ["Segunda", "Primera"], timeout=10000)
    bodies = request_bodies(patches)
    count_pending = column_count(page, "Pendiente")

    checks = {
        "orden inicial Primera, Segunda": initial_order == ["Primera", "Segunda"],
        "se emitió un PATCH de reordenamiento": len(bodies) == 1,
        "el PATCH usa el estado Pendiente y posición 0": bodies
        == [{"status": "Pendiente", "position": 0}],
        "el orden visible queda Segunda, Primera": final_order
        == ["Segunda", "Primera"],
        "la columna conserva las dos tarjetas": count_pending == "2",
    }
    obtained = (
        f"orden inicial={initial_order}; PATCH={bodies}; "
        f"orden final={final_order}; contador Pendiente={count_pending!r}"
    )
    return make_result(
        "CP-UI-04",
        checks,
        obtained,
        "Condición de borde: soltar en la misma columna reordena emitiendo "
        "un PATCH con la posición calculada.",
    )


def request_bodies_safe(requests: list) -> list[dict]:
    import json

    bodies = []
    for request in requests:
        try:
            bodies.append(json.loads(request.post_data or "{}"))
        except Exception:  # noqa: BLE001
            bodies.append({})
    return bodies


def ui_05(page, task) -> dict:
    puts = track_requests(page, "PUT", "/api/tasks/")
    open_detail(page, task["id"])

    page.click('[data-testid="edit-start"]')
    page.wait_for_selector('[data-testid="edit-task-title"]', timeout=5000)
    page.fill('[data-testid="edit-task-title"]', "Tarea corregida")
    page.fill('[data-testid="edit-task-description"]', "Descripción nueva")
    page.click('[data-testid="edit-save"]')

    page.wait_for_function(
        "() => document.querySelector('#task-detail-title')?.textContent "
        "=== 'Tarea corregida'",
        timeout=10000,
    )
    page.wait_for_timeout(300)

    puts_done = len(puts)
    detail_title = page.inner_text("#task-detail-title").strip()
    detail_description = page.inner_text(".detail__description").strip()
    board_titles = column_titles(page, task["status"])

    checks = {
        "se emitió un PUT": puts_done == 1,
        "el detalle muestra el título nuevo": detail_title == "Tarea corregida",
        "el detalle muestra la descripción nueva": detail_description
        == "Descripción nueva",
        "la tarjeta del tablero refleja el título": board_titles == ["Tarea corregida"],
    }
    obtained = (
        f"PUT={puts_done}; título del detalle={detail_title!r}; "
        f"descripción={detail_description!r}; tarjetas={board_titles}"
    )
    return make_result(
        "CP-UI-05",
        checks,
        obtained,
        "Edición desde el detalle con actualización del tablero.",
    )


def ui_06(page, task) -> dict:
    open_detail(page, task["id"])
    panel = checklist_panel(page)
    counter = panel.locator(".panel__counter")

    page.fill('[data-testid="subtask-input"]', "Paso 1")
    page.click('[data-testid="subtask-add"]')
    page.wait_for_function(
        "() => document.querySelectorAll('.checklist__item').length === 1",
        timeout=10000,
    )

    page.fill('[data-testid="subtask-input"]', "Paso 2")
    page.click('[data-testid="subtask-add"]')
    page.wait_for_function(
        "() => document.querySelectorAll('.checklist__item').length === 2",
        timeout=10000,
    )
    initial_counter = wait_text(counter, "0/2", timeout=5.0)
    items = page.locator(".checklist__item").count()

    item_one = page.locator(".checklist__item", has_text="Paso 1")
    item_one.locator('input[type="checkbox"]').click()
    page.wait_for_function(
        "() => {"
        "  const item = [...document.querySelectorAll('.checklist__item')]"
        "    .find((li) => li.textContent.includes('Paso 1'));"
        "  return Boolean(item && item.querySelector('input[type=checkbox]').checked);"
        "}",
        timeout=10000,
    )
    marked_counter = wait_text(counter, "1/2", timeout=10000)
    card_badge = (
        page.locator('[data-testid="checklist-badge"]').first.inner_text().strip()
    )

    item_two = page.locator(".checklist__item", has_text="Paso 2")
    item_two.locator("button.icon-button").click()
    final_counter = wait_text(counter, "1/1", timeout=10000)
    final_badge = (
        page.locator('[data-testid="checklist-badge"]').first.inner_text().strip()
    )

    checks = {
        "se listan las dos subtareas": items == 2,
        "el contador inicial es 0/2": initial_counter == "0/2",
        "el contador pasa a 1/2 al marcar": marked_counter == "1/2",
        "la tarjeta muestra la insignia 1/2 subtareas": card_badge == "1/2 subtareas",
        "el contador pasa a 1/1 al eliminar": final_counter == "1/1",
        "la insignia final es 1/1 subtareas": final_badge == "1/1 subtareas",
    }
    obtained = (
        f"subtareas listadas={items}; contador inicial={initial_counter!r}; "
        f"contador al marcar={marked_counter!r}; insignia={card_badge!r}; "
        f"contador al eliminar={final_counter!r}; insignia final={final_badge!r}"
    )
    return make_result(
        "CP-UI-06",
        checks,
        obtained,
        "Alta, marcado y eliminación de subtareas con el avance reflejado "
        "en el detalle y en la tarjeta.",
    )


def ui_07(page, task) -> dict:
    content = b"A" * 1024
    open_detail(page, task["id"])
    panel = attachments_panel(page)

    page.set_input_files(
        '[data-testid="attachment-input"]',
        {"name": "acta.txt", "mimeType": "text/plain", "buffer": content},
    )
    counter = wait_text(panel.locator(".panel__counter"), "1/3", timeout=15000)

    link = page.locator(".attachments__name").first
    link_text = link.inner_text().strip()
    files_badge = page.locator('[data-testid="files-badge"]').first.inner_text().strip()
    download_name, download_bytes = fetch_download(page, link)

    checks = {
        "el contador de adjuntos muestra 1/3": counter == "1/3",
        "aparece el enlace con el nombre original": link_text == "acta.txt",
        "la tarjeta muestra la insignia 1 archivo": files_badge == "1 archivo",
        "la descarga conserva el nombre original": download_name == "acta.txt",
        "el contenido descargado coincide": download_bytes == content,
    }
    obtained = (
        f"contador={counter!r}; enlace={link_text!r}; insignia={files_badge!r}; "
        f"nombre descargado={download_name!r}; bytes descargados="
        f"{len(download_bytes)}"
    )
    return make_result(
        "CP-UI-07",
        checks,
        obtained,
        "Subida de un archivo de 1 KB y descarga con el nombre original.",
    )


def ui_08(page, task) -> dict:
    title = task["title"]
    deletes = track_requests(page, "DELETE", "/api/tasks/")

    card(page, task["id"]).locator('[data-testid="task-delete"]').click()
    page.wait_for_selector('[data-testid="confirm-dialog"]', timeout=5000)
    dialog_text = page.inner_text("#confirm-message")
    cancel_present = page.locator('[data-testid="confirm-cancel"]').count() == 1

    page.click('[data-testid="confirm-accept"]')
    card(page, task["id"]).wait_for(state="detached", timeout=10000)
    page.wait_for_selector('[data-testid="toast"]', timeout=5000)
    toast_text = page.inner_text('[data-testid="toast"]')
    deletes_done = len(deletes)
    remaining = page.locator(".task").count()

    page.click('[data-testid="toast-action"]')
    card(page, task["id"]).wait_for(state="visible", timeout=10000)
    restored = card(page, task["id"]).count() == 1

    reload_board(page)
    persisted = task_in(page, "Pendiente", title).count() == 1

    checks = {
        "se abre el diálogo de confirmación": cancel_present,
        "el diálogo menciona el título de la tarea": title in dialog_text,
        "se emitió un DELETE": deletes_done >= 1,
        "la tarjeta desaparece del tablero": remaining == 0,
        "el aviso ofrece Deshacer": "Deshacer" in toast_text,
        "deshacer restaura la tarjeta": restored,
        "la tarea restaurada persiste": persisted,
    }
    obtained = (
        f"diálogo={dialog_text!r}; DELETE={deletes_done}; "
        f"tarjetas restantes={remaining}; aviso={toast_text!r}; "
        f"restaurada={restored}; persistió={persisted}"
    )
    return make_result(
        "CP-UI-08",
        checks,
        obtained,
        "Borrado lógico con confirmación previa y restauración desde el aviso.",
    )


def ui_09(page, _prepared) -> dict:
    title = "Tarea con prioridad y responsable"
    page.fill(FORM_TITLE, title)
    page.select_option('[data-testid="new-task-priority"]', "Alta")
    page.fill('[data-testid="new-task-assignee"]', "Ana")
    page.click(FORM_SUBMIT)

    card_locator = task_in(page, "Pendiente", title)
    card_locator.wait_for(timeout=10000)

    badge = card_locator.locator('[data-testid="priority-badge"]').inner_text().strip()
    assignee = card_locator.locator('[data-testid="task-assignee"]').inner_text().strip()

    checks = {
        "la tarjeta se creó en Pendiente": card_locator.count() == 1,
        "la insignia de prioridad muestra Alta": badge == "Alta",
        "el responsable se muestra en la tarjeta": assignee == "Ana",
    }
    obtained = f"insignia={badge!r}; responsable={assignee!r}"
    return make_result(
        "CP-UI-09",
        checks,
        obtained,
        "Alta desde el formulario con prioridad y responsable; verifica la tarjeta.",
    )


def prepare_search():
    return {
        "match": create_task("Informe de ventas", "Detalle del informe"),
        "other": create_task("Reunión de equipo", "Coordinar la reunión"),
    }


def ui_10(page, _prepared) -> dict:
    page.wait_for_function(
        "() => document.querySelectorAll('.task').length === 2", timeout=10000
    )
    page.fill('[data-testid="task-search"]', "informe")
    page.wait_for_function(
        "() => document.querySelectorAll('.task').length === 1", timeout=10000
    )

    visible_titles = page.eval_on_selector_all(
        '[data-testid="task-title"]', "elements => elements.map((e) => e.textContent)"
    )
    summary = page.inner_text('[data-testid="task-count"]').strip()
    other_visible = page.locator(".task", has_text="Reunión de equipo").count()

    checks = {
        "queda una sola tarjeta": len(visible_titles) == 1,
        "la tarjeta visible coincide": visible_titles == ["Informe de ventas"],
        "la tarjeta ajena desaparece": other_visible == 0,
        "el resumen muestra 1 tarea": summary == "1 tarea",
    }
    obtained = f"tarjetas visibles={visible_titles}; resumen={summary!r}"
    return make_result(
        "CP-UI-10",
        checks,
        obtained,
        "Búsqueda por texto desde la interfaz.",
    )


def ui_11(page, task) -> dict:
    title = task["title"]
    drag_task(page, task["id"], "En curso")
    task_in(page, "En curso", title).wait_for(timeout=10000)

    open_detail(page, task["id"])
    page.wait_for_selector('[data-testid="activity-timeline"]', timeout=10000)
    entries = page.locator(
        '[data-testid="activity-timeline"] .timeline__item'
    ).count()
    actions = page.eval_on_selector_all(
        '[data-testid="activity-timeline"] .timeline__action',
        "elements => elements.map((e) => e.textContent)",
    )

    checks = {
        "la tarjeta se movió a En curso": task_in(page, "En curso", title).count() == 1,
        "la cronología está visible": page.locator(
            '[data-testid="activity-timeline"]'
        ).count()
        == 1,
        "hay al menos una entrada": entries >= 1,
        "el movimiento quedó registrado": any(
            "Movida a En curso" in action for action in actions
        ),
    }
    obtained = f"entradas={entries}; acciones={actions}"
    return make_result(
        "CP-UI-11",
        checks,
        obtained,
        "Historial visible en el detalle después de mover la tarea.",
    )


CASES = [
    ("CP-UI-01", ui_01, None),
    ("CP-UI-02", ui_02, None),
    ("CP-UI-03", ui_03, prepare_single("Mover desde interfaz")),
    ("CP-UI-04", ui_04, prepare_pair),
    ("CP-UI-05", ui_05, prepare_single("Tarea original", "Descripción original")),
    ("CP-UI-06", ui_06, prepare_single("Checklist desde interfaz")),
    ("CP-UI-07", ui_07, prepare_single("Adjuntos desde interfaz")),
    ("CP-UI-08", ui_08, prepare_single("Eliminar desde interfaz")),
    ("CP-UI-09", ui_09, None),
    ("CP-UI-10", ui_10, prepare_search),
    ("CP-UI-11", ui_11, prepare_single("Mover y ver historial")),
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
