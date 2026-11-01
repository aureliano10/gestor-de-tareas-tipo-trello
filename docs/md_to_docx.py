"""Convierte un documento Markdown simple a .docx usando python-docx.

Soporta encabezados (#), listas con viñetas, listas numeradas, tablas y
negritas en línea (**texto**). Pensado para los entregables de cada etapa.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt


INLINE_RE = re.compile(r"(\*\*.+?\*\*|`[^`]+`)")
NUMBERED_RE = re.compile(r"^\d+\.\s+")


def add_inline(paragraph, text: str) -> None:
    position = 0
    for match in INLINE_RE.finditer(text):
        if match.start() > position:
            paragraph.add_run(text[position : match.start()])
        token = match.group(0)
        if token.startswith("**"):
            run = paragraph.add_run(token[2:-2])
            run.bold = True
        else:
            run = paragraph.add_run(token[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(9.5)
        position = match.end()
    if position < len(text):
        paragraph.add_run(text[position:])


def parse_table_row(line: str) -> list[str]:
    cells = line.strip().strip("|").split("|")
    return [cell.strip() for cell in cells]


def is_separator(line: str) -> bool:
    return bool(re.fullmatch(r"\|?[\s:\-|]+\|?", line.strip())) and "-" in line


def convert(markdown_path: Path, docx_path: Path) -> None:
    lines = markdown_path.read_text(encoding="utf-8").splitlines()
    document = Document()

    normal_style = document.styles["Normal"]
    normal_style.font.name = "Calibri"
    normal_style.font.size = Pt(11)

    index = 0
    in_code = False
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code = not in_code
            index += 1
            continue

        if in_code:
            paragraph = document.add_paragraph()
            run = paragraph.add_run(line.rstrip())
            run.font.name = "Consolas"
            run.font.size = Pt(9.5)
            index += 1
            continue

        if not stripped:
            index += 1
            continue

        if stripped.startswith("|"):
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1

            data_rows = [
                parse_table_row(row)
                for row in table_lines
                if not is_separator(row)
            ]
            if data_rows:
                columns = max(len(row) for row in data_rows)
                table = document.add_table(
                    rows=len(data_rows), cols=columns
                )
                table.style = "Table Grid"
                for row_index, row in enumerate(data_rows):
                    for col_index in range(columns):
                        cell = table.cell(row_index, col_index)
                        value = row[col_index] if col_index < len(row) else ""
                        cell.text = ""
                        paragraph = cell.paragraphs[0]
                        add_inline(paragraph, value)
                        if row_index == 0:
                            for run in paragraph.runs:
                                run.bold = True
                document.add_paragraph()
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            level = len(heading.group(1))
            document.add_heading(heading.group(2), level=min(level, 4))
            index += 1
            continue

        if stripped.startswith(("- ", "* ")):
            paragraph = document.add_paragraph(style="List Bullet")
            add_inline(paragraph, stripped[2:])
            index += 1
            continue

        if NUMBERED_RE.match(stripped):
            content = NUMBERED_RE.sub("", stripped, count=1)
            paragraph = document.add_paragraph(style="List Number")
            add_inline(paragraph, content)
            index += 1
            continue

        paragraph = document.add_paragraph()
        add_inline(paragraph, stripped)
        index += 1

    document.save(docx_path)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Uso: python md_to_docx.py entrada.md salida.docx")
    markdown_path = Path(sys.argv[1])
    docx_path = Path(sys.argv[2])
    convert(markdown_path, docx_path)
    print(f"Generado: {docx_path}")


if __name__ == "__main__":
    main()
