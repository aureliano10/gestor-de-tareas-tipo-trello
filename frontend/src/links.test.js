import { describe, it, expect } from "vitest";
import {
  MAX_LINKS,
  MAX_LINK_LABEL_LENGTH,
  MAX_LINK_URL_LENGTH,
  validateLink,
} from "./links.js";

describe("validateLink", () => {
  it("rechaza una URL vacía", () => {
    expect(validateLink({ url: "   " })).toBe("Ingresá una URL para el enlace.");
    expect(validateLink({})).toBe("Ingresá una URL para el enlace.");
  });

  it("exige el esquema http o https", () => {
    expect(validateLink({ url: "ejemplo.com" })).toBe(
      "El enlace debe comenzar con http:// o https://.",
    );
    expect(validateLink({ url: "ftp://ejemplo.com" })).toBe(
      "El enlace debe comenzar con http:// o https://.",
    );
  });

  it("acepta http y https sin distinguir mayúsculas", () => {
    expect(validateLink({ url: "http://ejemplo.com" })).toBe("");
    expect(validateLink({ url: "HTTPS://EJEMPLO.COM" })).toBe("");
  });

  it("limita la longitud de la URL", () => {
    const larga = `https://e.com/${"a".repeat(MAX_LINK_URL_LENGTH)}`;
    expect(validateLink({ url: larga })).toBe(
      `El enlace no puede superar los ${MAX_LINK_URL_LENGTH} caracteres.`,
    );
  });

  it("limita la longitud del nombre", () => {
    const label = "a".repeat(MAX_LINK_LABEL_LENGTH + 1);
    expect(validateLink({ url: "https://e.com", label })).toBe(
      `El nombre del enlace no puede superar los ${MAX_LINK_LABEL_LENGTH} caracteres.`,
    );
  });

  it("rechaza enlaces duplicados sin distinguir mayúsculas", () => {
    const existing = [{ url: "https://Ejemplo.com/doc" }];
    expect(validateLink({ url: "https://ejemplo.com/doc", existing })).toBe(
      "El enlace ya está agregado a la tarea.",
    );
  });

  it("limita la cantidad de enlaces", () => {
    const existing = Array.from({ length: MAX_LINKS }, (_, index) => ({
      url: `https://e.com/${index}`,
    }));
    expect(validateLink({ url: "https://e.com/nuevo", existing })).toBe(
      `Una tarea no puede tener más de ${MAX_LINKS} enlaces.`,
    );
  });

  it("devuelve cadena vacía para un enlace válido", () => {
    expect(validateLink({ url: "  https://ejemplo.com  ", label: "  Doc  " })).toBe(
      "",
    );
  });
});
