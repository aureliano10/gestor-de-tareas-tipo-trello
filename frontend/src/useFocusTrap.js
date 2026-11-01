import { useEffect, useRef } from "react";

const FOCUSABLE_SELECTOR = [
  "a[href]",
  "button:not([disabled])",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  '[tabindex]:not([tabindex="-1"])',
].join(", ");

/**
 * Atrapa el foco dentro del contenedor (trampa de Tab), enfoca el primer
 * control al abrir y restaura el foco al elemento que estaba activo antes.
 * `onEscape` se lee siempre actualizado, por lo que no reinicia la trampa.
 */
export function useFocusTrap(containerRef, { onEscape } = {}) {
  const escapeRef = useRef(onEscape);
  escapeRef.current = onEscape;

  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return undefined;
    }
    const previous = document.activeElement;

    function focusableItems() {
      return [...container.querySelectorAll(FOCUSABLE_SELECTOR)].filter(
        (element) => element.offsetParent !== null || element === document.activeElement,
      );
    }

    const items = focusableItems();
    (items[0] ?? container).focus();

    function handleKey(event) {
      if (event.key === "Escape") {
        event.stopPropagation();
        escapeRef.current?.();
        return;
      }
      if (event.key !== "Tab") {
        return;
      }
      const focusables = focusableItems();
      if (focusables.length === 0) {
        event.preventDefault();
        return;
      }
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    container.addEventListener("keydown", handleKey);
    return () => {
      container.removeEventListener("keydown", handleKey);
      if (previous instanceof HTMLElement && previous.isConnected) {
        previous.focus();
      }
    };
  }, [containerRef]);
}
