"""Ejecuta las pruebas unitarias de la Etapa 8 y guarda las evidencias.

Corre pytest sobre los módulos unitarios con salida detallada y XML de
JUnit, guarda el log completo en texto y arma un JSON con los casos
evaluados y su resultado.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "docs" / "evidencias" / "etapa_8"
TEST_FILES = [
    "backend/tests/test_unit_schemas.py",
    "backend/tests/test_unit_repository.py",
    "backend/tests/test_unit_database.py",
]

CASES = {
    "CP-UN-01": ("clean_title", "Recorte de espacios externos y texto válido."),
    "CP-UN-02": ("clean_title", "Límites de longitud (1, 100, 101) y vacíos."),
    "CP-UN-03": ("clean_description", "Campo opcional y límite (500, 501)."),
    "CP-UN-04": ("clean_priority", "Conjunto permitido y valores inválidos."),
    "CP-UN-05": ("clean_assignee", "Opcional, recorte y límite (60, 61)."),
    "CP-UN-06": ("clean_tag", "Vacía, solo espacios y límite (30, 31)."),
    "CP-UN-07": ("clean_tags", "Deduplicación sin distinguir mayúsculas."),
    "CP-UN-08": ("clean_link_url", "Esquema http/https y límite (500, 501)."),
    "CP-UN-09": ("clean_link_label", "Opcional, recorte y límite (60, 61)."),
    "CP-UN-10": ("_resolve_tag_id", "Reutiliza etiquetas sin distinguir mayúsculas."),
    "CP-UN-11": ("_set_tags", "Deduplica y aplica el límite de 5 etiquetas."),
    "CP-UN-12": ("_normalize_links", "Acepta dict/objeto, duplicados y límite 5."),
    "CP-UN-13": ("create_task", "Límite de subtareas en el alta (20, 21)."),
    "CP-UN-14": ("move_task", "Bloqueo de finalización con subtareas pendientes."),
    "CP-UN-15": ("create_attachment", "Límite de adjuntos por tarea (3, 4)."),
    "CP-UN-16": ("init_db", "Crea las siete tablas del esquema."),
    "CP-UN-17": ("init_db", "Migración aditiva de una tabla tasks incompleta."),
    "CP-UN-18": ("connection", "Revierte la transacción ante una excepción."),
}


def case_id(name: str) -> str:
    match = re.search(r"cp_[a-z]+_\d+", name)
    return match.group(0).upper().replace("_", "-") if match else name


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    junit_path = Path(tempfile.mkdtemp()) / "unitarias.xml"

    command = [
        sys.executable,
        "-m",
        "pytest",
        *TEST_FILES,
        "-v",
        f"--junit-xml={junit_path}",
    ]
    process = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True, check=False
    )
    output = process.stdout + process.stderr
    (EVIDENCE_DIR / "pytest_salida.txt").write_text(output, encoding="utf-8")

    root = ET.parse(junit_path).getroot()
    cases = []
    for testcase in root.iter("testcase"):
        identifier = case_id(testcase.get("name", ""))
        failed = (
            testcase.find("failure") is not None
            or testcase.find("error") is not None
        )
        function, description = CASES.get(identifier, ("-", "-"))
        cases.append(
            {
                "id": identifier,
                "funcion": function,
                "descripcion": description,
                "test": testcase.get("name"),
                "archivo": testcase.get("classname"),
                "duracion_s": float(testcase.get("time", "0")),
                "estado": "Fallido" if failed else "Aprobado",
            }
        )
    cases.sort(key=lambda item: item["id"])

    passed = sum(1 for item in cases if item["estado"] == "Aprobado")
    report = {
        "total": len(cases),
        "aprobados": passed,
        "fallidos": len(cases) - passed,
        "casos": cases,
    }
    (EVIDENCE_DIR / "resultados_unitarias.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    for item in cases:
        print(f"{item['id']}: {item['estado'].upper()} | {item['funcion']}")
    print(f"\nUnitarias: {passed}/{len(cases)} aprobados")
    return 0 if process.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
