"""Recalcula los ratios de contraste WCAG 2.x tras la corrección de la auditoría.

Se evalúan los pares de color relevantes del tema claro y oscuro de
`frontend/src/styles/app.css`, incluido el compuesto de colores con alfa y de
`color-mix(in srgb, ...)` en espacio sRGB. Umbrales: 4.5:1 texto normal,
3:1 texto grande y componentes/indicadores no textuales (WCAG 1.4.3, 1.4.11,
2.4.11, 2.5.8).

Uso: python calcular_contraste_corregido.py
"""

from __future__ import annotations


def srgb_to_linear(channel: float) -> float:
    channel /= 255
    if channel <= 0.04045:
        return channel / 12.92
    return ((channel + 0.055) / 1.055) ** 2.4


def luminance(rgb: tuple[float, float, float]) -> float:
    r, g, b = (srgb_to_linear(value) for value in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def hexa(value: str) -> tuple[float, float, float]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def composite(
    fg: tuple[float, float, float], alpha: float, bg: tuple[float, float, float]
) -> tuple[float, float, float]:
    return tuple(alpha * f + (1 - alpha) * b for f, b in zip(fg, bg))  # type: ignore[return-value]


def mix(
    a: tuple[float, float, float], a_ratio: float, b: tuple[float, float, float]
) -> tuple[float, float, float]:
    return tuple(a_ratio * x + (1 - a_ratio) * y for x, y in zip(a, b))  # type: ignore[return-value]


def line(label: str, fg, bg, threshold: float) -> str:
    ratio = contrast(fg, bg)
    ok = "OK   " if ratio >= threshold else "FALLA"
    return f"{ok} {ratio:5.2f}:1 (umbral {threshold})  {label}"


def main() -> None:
    # --- Tokens del tema claro ---
    surface = hexa("#ffffff")
    surface2 = hexa("#f6f8fd")
    surface3 = hexa("#eceffa")
    bg = hexa("#eef1f9")
    text = hexa("#14182b")
    text_soft = hexa("#4a5169")
    muted = hexa("#5c6379")
    primary = hexa("#5b53e8")
    primary_dark = hexa("#443ccd")
    focus = hexa("#443ccd")
    border_control = hexa("#7c829b")
    danger_strong = hexa("#c2262b")
    info_strong = hexa("#1d4ed8")
    btn_from = hexa("#5b53e8")
    btn_to = hexa("#443ccd")
    btn_danger_from = hexa("#d1343a")
    btn_danger_to = hexa("#a82026")
    danger_soft = hexa("#fdeeee")

    print("=== MODO CLARO ===")
    print(line("texto principal #14182b sobre surface", text, surface, 4.5))
    print(line("texto suave #4a5169 sobre surface", text_soft, surface, 4.5))
    print(line("CORREGIDO --muted #5c6379 sobre surface #fff", muted, surface, 4.5))
    print(line("CORREGIDO --muted #5c6379 sobre bg #eef1f9", muted, bg, 4.5))
    print(line("CORREGIDO --muted #5c6379 sobre surface-2 #f6f8fd", muted, surface2, 4.5))
    print(line("CORREGIDO --muted #5c6379 sobre surface-3 #eceffa", muted, surface3, 4.5))
    print(line("blanco sobre botón gradiente arriba #5b53e8", surface, btn_from, 4.5))
    print(line("blanco sobre botón gradiente abajo #443ccd", surface, btn_to, 4.5))
    print(line("blanco sobre botón peligro arriba #d1343a", surface, btn_danger_from, 4.5))
    print(line("blanco sobre botón peligro abajo #a82026", surface, btn_danger_to, 4.5))
    print(line("CORREGIDO error #c2262b sobre surface #fff", danger_strong, surface, 4.5))
    print(line("CORREGIDO error #c2262b sobre surface-2 #f6f8fd", danger_strong, surface2, 4.5))
    print(line("CORREGIDO alerta #c2262b sobre danger-soft #fdeeee", danger_strong, danger_soft, 4.5))
    print(
        line(
            "CORREGIDO badge prioridad Alta #c2262b sobre mix(danger,16%)",
            danger_strong,
            mix(hexa("#e5484d"), 0.16, surface),
            4.5,
        )
    )
    print(
        line(
            "CORREGIDO badge prioridad Media #1d4ed8 sobre mix(progress,16%)",
            info_strong,
            mix(hexa("#3b82f6"), 0.16, surface),
            4.5,
        )
    )
    print(line("enlaces/ghost #443ccd sobre surface", primary_dark, surface, 4.5))
    print(line("anillo de foco #443ccd sobre surface (1.4.11)", focus, surface, 3.0))
    print(line("CORREGIDO borde control #7c829b sobre surface-2 #f6f8fd", border_control, surface2, 3.0))
    print(line("CORREGIDO borde control #7c829b sobre surface #fff", border_control, surface, 3.0))
    print(line("CORREGIDO borde control #7c829b sobre surface-3 #eceffa", border_control, surface3, 3.0))
    print(line("badge vence pronto #b45309 sobre #fff4e5", hexa("#b45309"), hexa("#fff4e5"), 4.5))
    print(line("badge completo #067647 sobre #e7f8ef", hexa("#067647"), hexa("#e7f8ef"), 4.5))
    print(line("badge archivos #6435c9 sobre #f0edff", hexa("#6435c9"), hexa("#f0edff"), 4.5))
    print(line("onboarding chip primary-dark #443ccd sobre primary-soft", primary_dark, mix(primary, 0.12, surface), 4.5))

    print()
    print("=== MODO OSCURO ===")
    dark_surface = hexa("#161a2e")
    dark_surface2 = hexa("#1c2137")
    dark_bg = hexa("#0d1020")
    dark_text = hexa("#eef1fb")
    dark_text_soft = hexa("#c3c9e2")
    dark_muted = hexa("#8f97b6")
    dark_border_control = hexa("#7c85b4")
    white = hexa("#ffffff")
    dark_btn_from = hexa("#4f46e5")
    dark_btn_to = hexa("#3730a3")
    dark_btn_danger_from = hexa("#d1353a")
    dark_btn_danger_to = hexa("#b3272c")
    dark_focus = hexa("#8b83ff")
    dark_primary = hexa("#8b83ff")
    dark_alert_bg = composite(hexa("#ff6b70"), 0.14, dark_surface)
    dark_alert_fg = hexa("#ffb4b6")

    print(line("texto principal #eef1fb sobre surface", dark_text, dark_surface, 4.5))
    print(line("texto suave #c3c9e2 sobre surface", dark_text_soft, dark_surface, 4.5))
    print(line("muted #8f97b6 sobre surface", dark_muted, dark_surface, 4.5))
    print(line("muted #8f97b6 sobre bg #0d1020", dark_muted, dark_bg, 4.5))
    print(line("CORREGIDO blanco sobre botón arriba #4f46e5", white, dark_btn_from, 4.5))
    print(line("CORREGIDO blanco sobre botón abajo #3730a3", white, dark_btn_to, 4.5))
    print(line("CORREGIDO blanco sobre botón peligro arriba #d1353a", white, dark_btn_danger_from, 4.5))
    print(line("CORREGIDO blanco sobre botón peligro abajo #b3272c", white, dark_btn_danger_to, 4.5))
    print(line("CORREGIDO alerta #ffb4b6 sobre danger-soft oscuro", dark_alert_fg, dark_alert_bg, 4.5))
    print(line("CORREGIDO borde control #7c85b4 sobre surface-2", dark_border_control, dark_surface2, 3.0))
    print(line("CORREGIDO borde control #7c85b4 sobre surface", dark_border_control, dark_surface, 3.0))
    print(line("anillo de foco #8b83ff sobre surface (1.4.11)", dark_focus, dark_surface, 3.0))
    print(line("badge vence pronto #fbbf24 sobre mix(pending,16%)", hexa("#fbbf24"), composite(hexa("#f59f0b"), 0.16, dark_surface), 4.5))
    print(line("badge completo #4ade80 sobre mix(done,18%)", hexa("#4ade80"), composite(hexa("#12a150"), 0.18, dark_surface), 4.5))
    print(line("badge archivos #c4b5fd sobre mix(primary,18%)", hexa("#c4b5fd"), composite(hexa("#8b83ff"), 0.18, dark_surface), 4.5))
    print(line("toast acción #a49cff sobre surface oscuro", hexa("#a49cff"), dark_surface, 4.5))
    print(line("toast cerrar #c3c9e2 sobre surface oscuro", dark_text_soft, dark_surface, 4.5))
    print(line("toast mensaje #eef1fb sobre surface oscuro", dark_text, dark_surface, 4.5))


if __name__ == "__main__":
    main()
