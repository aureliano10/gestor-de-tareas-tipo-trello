"""Ejecuta las pruebas de integración de la Etapa 9 y guarda las evidencias.

Corre pytest sobre el módulo de integración con salida detallada y XML de
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
EVIDENCE_DIR = ROOT / "docs" / "evidencias" / "etapa_9"
TEST_FILES = ["backend/tests/test_integration_flow.py"]

CASES = {
    "CP-IN-01": "Alta de tarea enriquecida y persistencia en SQLite.",
    "CP-IN-02": "Adjunto: subida, almacenamiento en disco y descarga.",
    "CP-IN-03": "Flujo de estados con la regla de finalización.",
    "CP-IN-04": "Reapertura automática al agregar una subtarea pendiente.",
    "CP-IN-05": "Lectura con filtros y orden del tablero.",
    "CP-IN-06": "Historial de actividad persistido y reordenado.",
}


def case_id(name: str) -> str:
    match = re.search(r"cp_[a-z]+_\d+", name)
    return match.group(0).upper().replace("_", "-") if match else name


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    junit_path = Path(tempfile.mkdtemp()) / "integracion.xml"

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
        cases.append(
            {
                "id": identifier,
                "descripcion": CASES.get(identifier, "-"),
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
    (EVIDENCE_DIR / "resultados_integracion.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    for item in cases:
        print(f"{item['id']}: {item['estado'].upper()} | {item['descripcion']}")
    print(f"\nIntegración: {passed}/{len(cases)} aprobados")
    return 0 if process.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
