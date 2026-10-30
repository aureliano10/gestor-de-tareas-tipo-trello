from __future__ import annotations

from pathlib import Path

from common import EVIDENCE_DIR

APP_URL = "http://127.0.0.1:5173/"
SCREENSHOT_DIR = EVIDENCE_DIR / "screenshots"


def open_page(browser, width: int = 1366, height: int = 900):
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    goto_board(page)
    return context, page


def goto_board(page) -> None:
    page.goto(APP_URL, wait_until="domcontentloaded")
    page.wait_for_selector(".column", timeout=15000)


def reload_board(page) -> None:
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector(".column", timeout=15000)


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


def drag_task(page, task_id: int, target_status: str) -> None:
    page.evaluate(
        """({ taskId, targetStatus }) => {
            const card = Array.from(document.querySelectorAll('.task')).find(
                (element) =>
                    element.querySelector('.task__id')?.textContent === '#' + taskId
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
                bubbles: true, cancelable: true, dataTransfer,
            }));
            column.dispatchEvent(new DragEvent('drop', {
                bubbles: true, cancelable: true, dataTransfer,
            }));
            card.dispatchEvent(
                new DragEvent('dragend', { bubbles: true, dataTransfer })
            );
        }""",
        {"taskId": task_id, "targetStatus": target_status},
    )


def drop_raw(page, raw_value: str, target_status: str) -> None:
    page.evaluate(
        """({ rawValue, targetStatus }) => {
            const column = document.querySelector(
                '.column[data-status="' + targetStatus + '"]'
            );
            if (!column) throw new Error('No se encontró la columna ' + targetStatus);
            const dataTransfer = new DataTransfer();
            dataTransfer.setData('text/plain', rawValue);
            column.dispatchEvent(new DragEvent('dragover', {
                bubbles: true, cancelable: true, dataTransfer,
            }));
            column.dispatchEvent(new DragEvent('drop', {
                bubbles: true, cancelable: true, dataTransfer,
            }));
        }""",
        {"rawValue": raw_value, "targetStatus": target_status},
    )


def set_input_value(page, value: str) -> None:
    page.evaluate(
        """(value) => {
            const input = document.querySelector('#task-title');
            input.maxLength = 255;
            const setter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value'
            ).set;
            setter.call(input, value);
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }""",
        value,
    )


def task_in(page, status: str, title: str):
    return page.locator(
        f'.column[data-status="{status}"] .task', has_text=title
    )
