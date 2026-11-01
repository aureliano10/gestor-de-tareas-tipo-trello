import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { useRef } from "react";
import { render, cleanup, fireEvent } from "@testing-library/react";
import { useFocusTrap } from "./useFocusTrap.js";

afterEach(cleanup);

function Trap({ onEscape }) {
  const ref = useRef(null);
  useFocusTrap(ref, { onEscape });
  return (
    <div ref={ref} tabIndex={-1} data-testid="trap">
      <button>Uno</button>
      <button>Dos</button>
    </div>
  );
}

function EmptyTrap() {
  const ref = useRef(null);
  useFocusTrap(ref, {});
  return (
    <div ref={ref} tabIndex={-1} data-testid="empty">
      Sin controles
    </div>
  );
}

// jsdom no implementa layout: `offsetParent` siempre es null, por lo que la
// trampa descartaría todos los controles. Se simula el comportamiento real.
let descriptor;
beforeEach(() => {
  descriptor = Object.getOwnPropertyDescriptor(HTMLElement.prototype, "offsetParent");
  Object.defineProperty(HTMLElement.prototype, "offsetParent", {
    configurable: true,
    get() {
      return this.parentElement;
    },
  });
});

afterEach(() => {
  if (descriptor) {
    Object.defineProperty(HTMLElement.prototype, "offsetParent", descriptor);
  } else {
    delete HTMLElement.prototype.offsetParent;
  }
});

describe("useFocusTrap", () => {
  it("enfoca el primer control al montar", () => {
    const { getByText } = render(<Trap />);
    expect(document.activeElement).toBe(getByText("Uno"));
  });

  it("mueve Tab del último control al primero", () => {
    const { getByText } = render(<Trap />);
    const first = getByText("Uno");
    const last = getByText("Dos");
    last.focus();
    fireEvent.keyDown(last, { key: "Tab" });
    expect(document.activeElement).toBe(first);
  });

  it("mueve Shift+Tab del primer control al último", () => {
    const { getByText } = render(<Trap />);
    const first = getByText("Uno");
    const last = getByText("Dos");
    first.focus();
    fireEvent.keyDown(first, { key: "Tab", shiftKey: true });
    expect(document.activeElement).toBe(last);
  });

  it("invoca onEscape al presionar Escape", () => {
    const onEscape = vi.fn();
    const { getByText } = render(<Trap onEscape={onEscape} />);
    fireEvent.keyDown(getByText("Uno"), { key: "Escape" });
    expect(onEscape).toHaveBeenCalledTimes(1);
  });

  it("ignora las teclas que no son Tab ni Escape", () => {
    const { getByText } = render(<Trap />);
    const first = getByText("Uno");
    first.focus();
    fireEvent.keyDown(first, { key: "a" });
    expect(document.activeElement).toBe(first);
  });

  it("restaura el foco previo al desmontar", () => {
    const outside = document.createElement("button");
    document.body.appendChild(outside);
    outside.focus();

    const { unmount } = render(<Trap />);
    unmount();

    expect(document.activeElement).toBe(outside);
    outside.remove();
  });

  it("bloquea Tab cuando no hay controles enfocables", () => {
    const { getByTestId } = render(<EmptyTrap />);
    const container = getByTestId("empty");
    const noCancelado = fireEvent.keyDown(container, { key: "Tab" });
    expect(noCancelado).toBe(false);
  });
});
