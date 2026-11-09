from __future__ import annotations

import os
import re
import time
from pathlib import Path

from common import EVIDENCE_DIR

APP_URL = "http://127.0.0.1:5173/"
SCREENSHOT_DIR = EVIDENCE_DIR / "screenshots"

FORM_OPEN = '[data-testid="new-task-open"]'
FORM_MODAL = '[data-testid="task-form-modal"]'
FORM_TITLE = '[data-testid="new-task-title"]'
FORM_DESCRIPTION = '[data-testid="new-task-description"]'
FORM_DUE = '[data-testid="new-task-due"]'
FORM_SUBMIT = '[data-testid="task-submit"]'
FORM_ERROR = '[data-testid="task-form-error"]'

DETAIL = '[data-testid="task-detail"]'


def open_page(browser, width: int = 1366, height: int = 900):
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    goto_board(page)
    return context, page


def launch_browser(playwright, *, headless: bool = True):
    """Lanza Chromium respetando la variable de entorno ``PLAYWRIGHT_CHANNEL``.

    Por defecto usa el canal ``chrome`` (el Chrome instalado en el sistema), que
    es lo que hay disponible en el entorno local. En integración continua se
    instala el Chromium incluido de Playwright y se ejecuta con
    ``PLAYWRIGHT_CHANNEL=chromium``. Un valor vacío lanza el navegador incluido
    sin canal explícito.
    """
    channel = os.environ.get("PLAYWRIGHT_CHANNEL", "chrome").strip() or None
    return playwright.chromium.launch(channel=channel, headless=headless)


def goto_board(page) -> None:
    page.goto(APP_URL, wait_until="domcontentloaded")
    page.wait_for_selector(".column", timeout=15000)


def reload_board(page) -> None:
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector(".column", timeout=15000)


def open_task_form(page) -> None:
    """Abre el modal de alta de tareas.

    El formulario ya no está siempre visible: se muestra en un modal que se
    abre desde el botón ``new-task-open`` y se cierra automáticamente al crear
    la tarea.
    """
    if page.locator(FORM_MODAL).count() > 0:
        return
    page.click(FORM_OPEN)
    page.wait_for_selector(FORM_MODAL, timeout=10000)
    page.wait_for_selector(FORM_TITLE, timeout=10000)


def screenshot(page, case_id: str) -> Path:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SCREENSHOT_DIR / f"{case_id}.png"
    page.screenshot(path=str(path), full_page=True)
    return path


def track_requests(page, method: str, fragment: str) -> list:
    captured = []

    def handler(request):
        if request.method == method and fragment in request.url:
            captured.append(request)

    page.on("request", handler)
    return captured


def request_bodies(requests: list) -> list[dict]:
    """Cuerpo JSON de cada petición capturada."""
    import json

    bodies = []
    for request in requests:
        try:
            bodies.append(json.loads(request.post_data or "{}"))
        except Exception:  # noqa: BLE001
            bodies.append({})
    return bodies


def drag_task(page, task_id: int, target_status: str, client_y: float = 0) -> None:
    """Arrastra la tarjeta hasta la columna indicada, soltando en `client_y`."""
    page.evaluate(
        """({ taskId, targetStatus, clientY }) => {
            const card = document.querySelector(
                '.task[data-task-id="' + taskId + '"]'
            );
            if (!card) throw new Error('No se encontró la tarjeta ' + taskId);
            const column = document.querySelector(
                '.column[data-status="' + targetStatus + '"]'
            );
            if (!column) throw new Error('No se encontró la columna ' + targetStatus);
            const dataTransfer = new DataTransfer();
            dataTransfer.setData('text/plain', String(taskId));
            card.dispatchEvent(
                new DragEvent('dragstart', { bubbles: true, dataTransfer })
            );
            column.dispatchEvent(new DragEvent('dragover', {
                bubbles: true, cancelable: true, dataTransfer, clientY,
            }));
            column.dispatchEvent(new DragEvent('drop', {
                bubbles: true, cancelable: true, dataTransfer, clientY,
            }));
            card.dispatchEvent(
                new DragEvent('dragend', { bubbles: true, dataTransfer })
            );
        }""",
        {"taskId": task_id, "targetStatus": target_status, "clientY": client_y},
    )


def drop_raw(page, raw_value: str, target_status: str, client_y: float = 0) -> None:
    """Simula un soltado con un identificador arbitrario, sin tarjeta origen."""
    page.evaluate(
        """({ rawValue, targetStatus, clientY }) => {
            const column = document.querySelector(
                '.column[data-status="' + targetStatus + '"]'
            );
            if (!column) throw new Error('No se encontró la columna ' + targetStatus);
            const dataTransfer = new DataTransfer();
            dataTransfer.setData('text/plain', rawValue);
            column.dispatchEvent(new DragEvent('dragover', {
                bubbles: true, cancelable: true, dataTransfer, clientY,
            }));
            column.dispatchEvent(new DragEvent('drop', {
                bubbles: true, cancelable: true, dataTransfer, clientY,
            }));
        }""",
        {"rawValue": raw_value, "targetStatus": target_status, "clientY": client_y},
    )


def set_field_value(
    page, selector: str, value: str, max_length: int | None = None
) -> None:
    """Carga un valor saltando el límite de `maxLength` para ejercitar las ramas."""
    page.evaluate(
        """({ selector, value, maxLength }) => {
            const field = document.querySelector(selector);
            if (!field) throw new Error('No se encontró el campo ' + selector);
            if (maxLength) {
                field.maxLength = maxLength;
            }
            const prototype = field.tagName === 'TEXTAREA'
                ? window.HTMLTextAreaElement.prototype
                : window.HTMLInputElement.prototype;
            const setter = Object.getOwnPropertyDescriptor(
                prototype, 'value'
            ).set;
            setter.call(field, value);
            field.dispatchEvent(new Event('input', { bubbles: true }));
        }""",
        {"selector": selector, "value": value, "maxLength": max_length},
    )


def set_input_value(page, value: str, max_length: int = 255) -> None:
    """Compatibilidad: carga el título del formulario de alta."""
    set_field_value(page, FORM_TITLE, value, max_length)


def task_in(page, status: str, title: str):
    return page.locator(f'.column[data-status="{status}"] .task', has_text=title)


def card(page, task_id: int):
    return page.locator(f'.task[data-task-id="{task_id}"]')


def column_titles(page, status: str) -> list[str]:
    return page.eval_on_selector_all(
        f'.column[data-status="{status}"] [data-testid="task-title"]',
        "elements => elements.map((element) => element.textContent)",
    )


def column_count(page, status: str) -> str:
    return page.inner_text(f'.column[data-status="{status}"] .column__count').strip()


def badge_text(page, test_id: str) -> str | None:
    locator = page.locator(f'[data-testid="{test_id}"]')
    if locator.count() == 0:
        return None
    return locator.first.text_content()


def open_detail(page, task_id: int) -> None:
    card(page, task_id).click()
    page.wait_for_selector(DETAIL, timeout=10000)


def checklist_panel(page):
    return page.locator(".panel", has=page.locator('[data-testid="subtask-input"]'))


def attachments_panel(page):
    return page.locator(".panel", has=page.locator('[data-testid="attachment-input"]'))


def wait_text(locator, expected: str, timeout: float = 10.0) -> str:
    """Espera a que el texto del localizador coincida y devuelve el último leído."""
    deadline = time.time() + timeout
    text = ""
    while time.time() < deadline:
        text = (locator.inner_text() or "").strip()
        if text == expected:
            return text
        time.sleep(0.1)
    return text


def wait_titles(
    page, status: str, expected: list[str], timeout: float = 10.0
) -> list[str]:
    """Espera a que el orden de los títulos de una columna coincida."""
    deadline = time.time() + timeout
    titles: list[str] = []
    while time.time() < deadline:
        titles = column_titles(page, status)
        if titles == expected:
            return titles
        time.sleep(0.1)
    return titles


def fetch_download(page, link) -> tuple[str, bytes]:
    """Descarga el enlace y devuelve (nombre sugerido, contenido)."""
    try:
        with page.expect_download(timeout=15000) as info:
            link.click()
        download = info.value
        return download.suggested_filename, Path(download.path()).read_bytes()
    except Exception:  # noqa: BLE001
        url = link.evaluate("element => element.href")
        response = page.request.get(url)
        disposition = response.headers.get("content-disposition", "")
        match = re.search(r'filename="?([^";]+)"?', disposition)
        return (match.group(1) if match else ""), response.body()
