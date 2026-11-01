/** Reglas de negocio de los enlaces de una tarea (compartidas por el alta y
 * el detalle). Centralizadas para que no se desincronicen entre formularios. */

export const MAX_LINKS = 5;
export const MAX_LINK_URL_LENGTH = 500;
export const MAX_LINK_LABEL_LENGTH = 60;

function isValidLink(url) {
  return /^https?:\/\//i.test(url);
}

/**
 * Valida un enlace nuevo contra los ya existentes.
 * Devuelve el mensaje de error o `""` si es válido.
 */
export function validateLink({ url, label, existing = [] }) {
  const cleanUrl = (url ?? "").trim();
  const cleanLabel = (label ?? "").trim();

  if (!cleanUrl) {
    return "Ingresá una URL para el enlace.";
  }
  if (!isValidLink(cleanUrl)) {
    return "El enlace debe comenzar con http:// o https://.";
  }
  if (cleanUrl.length > MAX_LINK_URL_LENGTH) {
    return `El enlace no puede superar los ${MAX_LINK_URL_LENGTH} caracteres.`;
  }
  if (cleanLabel.length > MAX_LINK_LABEL_LENGTH) {
    return `El nombre del enlace no puede superar los ${MAX_LINK_LABEL_LENGTH} caracteres.`;
  }
  if (
    existing.some(
      (link) => String(link.url).toLowerCase() === cleanUrl.toLowerCase(),
    )
  ) {
    return "El enlace ya está agregado a la tarea.";
  }
  if (existing.length >= MAX_LINKS) {
    return `Una tarea no puede tener más de ${MAX_LINKS} enlaces.`;
  }
  return "";
}
