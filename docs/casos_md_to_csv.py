"""Extrae las fichas de casos de Etapa_5.md y genera casos_de_prueba.csv.

Cada ficha se reconoce por un encabezado '### CP-...' y una lista de campos
con el formato '- Campo: valor'. Así el Markdown es la fuente de verdad.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

CASE_RE = re.compile(r"^###\s+(CP-[A-Z]+-\d+)\s*$")
FIELD_RE = re.compile(r"^-\s+([^:]+):\s*(.*)$")

FIELDS = [
    ("ID", "id"),
    ("Funcionalidad", "funcionalidad"),
    ("Objetivo", "objetivo"),
    ("Precondiciones", "precondiciones"),
    ("Datos de entrada", "datos_entrada"),
    ("Procedimiento", "procedimiento"),
    ("Resultado esperado", "resultado_esperado"),
    ("Resultado obtenido", "resultado_obtenido"),
    ("Estado", "estado"),
    ("Observaciones", "observaciones"),
    ("Técnica", "tecnica"),
    ("Requisito", "requisito"),
    ("Capa", "capa"),
]
FIELD_MAP = {label: key for label, key in FIELDS}
COLUMNS = [key for _, key in FIELDS]
TRAILING_PERIOD_FIELDS = {"id", "estado", "capa", "requisito"}


def parse(markdown_path: Path) -> list[dict]:
    rows: list[dict] = []
    current: dict | None = None

    def close_current() -> None:
        nonlocal current
        if current is not None:
            rows.append(current)
            current = None

    for line in markdown_path.read_text(encoding="utf-8").splitlines():
        case_match = CASE_RE.match(line.strip())
        if case_match:
            close_current()
            current = {"id": case_match.group(1)}
            continue

        if line.startswith("#"):
            close_current()
            continue

        if current is not None:
            field_match = FIELD_RE.match(line.strip())
            if field_match:
                key = FIELD_MAP.get(field_match.group(1).strip())
                if key:
                    value = field_match.group(2).strip().replace("`", "")
                    if key in TRAILING_PERIOD_FIELDS:
                        value = value.rstrip(".")
                    current[key] = value

    close_current()
    return rows


def validate(rows: list[dict]) -> None:
    if not rows:
        raise SystemExit("No se encontraron fichas de casos.")
    for row in rows:
        missing = [column for column in COLUMNS if not row.get(column)]
        if missing:
            raise SystemExit(
                f"Caso {row.get('id')} incompleto. Faltan: {', '.join(missing)}"
            )


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Uso: python casos_md_to_csv.py entrada.md salida.csv")

    markdown_path = Path(sys.argv[1])
    csv_path = Path(sys.argv[2])

    rows = parse(markdown_path)
    validate(rows)

    with csv_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generado: {csv_path} ({len(rows)} casos)")


if __name__ == "__main__":
    main()
