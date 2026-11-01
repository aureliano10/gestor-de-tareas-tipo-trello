from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "docs" / "evidencias" / "etapa_6"
ETAPA_5 = ROOT / "docs" / "Etapa_5.md"
SOURCE_FILES = [
    ("api", EVIDENCE_DIR / "resultados_api.json"),
    ("ui", EVIDENCE_DIR / "resultados_ui.json"),
    ("caja_blanca", EVIDENCE_DIR / "resultados_caja_blanca.json"),
]

INTRO_OLD = (
    "Esta etapa es de **diseño**. Los casos se documentan con todos sus campos y "
    "los campos `Resultado obtenido` y `Estado` quedan en `Pendiente` hasta que "
    "se ejecuten en la Etapa 6, donde se completan con los resultados reales."
)
INTRO_NEW = (
    "Esta etapa es de **diseño**. Los casos se documentan con todos sus campos. "
    "La ejecución y el registro de resultados se realizaron en la Etapa 6; por "
    "ese motivo, los campos `Resultado obtenido` y `Estado` reflejan los "
    "resultados de esa ejecución."
)

COVERAGE_OLD = (
    "La cobertura real se verifica durante la ejecución de la Etapa 6; las "
    "pruebas unitarias formales se incorporarán en la Etapa 8."
)
COVERAGE_NEW = (
    "La cobertura real se verificó durante la ejecución de la Etapa 6; las "
    "pruebas unitarias formales se incorporarán en la Etapa 8."
)

FICHE_UPDATES: dict[str, list[tuple[str, str]]] = {}


def load_results() -> dict[str, dict]:
    merged: dict[str, dict] = {}
    groups: dict[str, list[str]] = {}
    for group, path in SOURCE_FILES:
        data = json.loads(path.read_text(encoding="utf-8"))
        groups[group] = [item["id"] for item in data]
        for item in data:
            if item["id"] in merged:
                raise SystemExit(f"ID duplicado en los resultados: {item['id']}")
            merged[item["id"]] = item
    return merged, groups


def update_fiches(text: str, results: dict[str, dict]) -> str:
    for case_id, replacements in FICHE_UPDATES.items():
        for old, new in replacements:
            if new in text:
                continue
            if old not in text:
                raise SystemExit(
                    f"No se encontró el texto de diseño a reemplazar en {case_id}"
                )
            text = text.replace(old, new, 1)

    pattern = re.compile(
        r"(### (?P<id>CP-[A-Z]+-\d+)\n)(?P<body>.*?)(?=\n### CP-|\Z)",
        re.DOTALL,
    )

    def replace_block(match: re.Match) -> str:
        case_id = match.group("id")
        result = results.get(case_id)
        if result is None:
            raise SystemExit(f"Falta el resultado de {case_id}")
        body = match.group("body")
        obtained = result["resultado_obtenido"].strip()
        if not obtained.endswith("."):
            obtained += "."
        state = "Aprobado" if result["passed"] else "Fallido"
        body = re.sub(
            r"- Resultado obtenido: .*",
            lambda _match: f"- Resultado obtenido: {obtained}",
            body,
            count=1,
        )
        body = re.sub(
            r"- Estado: .*",
            lambda _match: f"- Estado: {state}.",
            body,
            count=1,
        )
        return f"{match.group(1)}{body}"

    text = pattern.sub(replace_block, text)

    states = {
        case_id: "Aprobado" if result["passed"] else "Fallido"
        for case_id, result in results.items()
    }
    lines = text.splitlines()
    for index, line in enumerate(lines):
        row = re.match(r"\| (CP-[A-Z]+-\d+) \|", line)
        if row:
            case_id = row.group(1)
            if case_id not in states:
                raise SystemExit(f"Fila de resumen sin resultado: {case_id}")
            lines[index] = re.sub(
                r"\|\s*(Pendiente|Aprobado|Fallido)\s*\|\s*$",
                f"| {states[case_id]} |",
                line,
            )
    return "\n".join(lines) + "\n"


def main() -> int:
    results, groups = load_results()
    expected = (
        {f"CP-CRE-{index:02d}" for index in range(1, 10)}
        | {f"CP-MOV-{index:02d}" for index in range(1, 6)}
        | {f"CP-EDI-{index:02d}" for index in range(1, 4)}
        | {f"CP-SUB-{index:02d}" for index in range(1, 5)}
        | {f"CP-BLO-{index:02d}" for index in range(1, 5)}
        | {"CP-FEC-01", "CP-FEC-02"}
        | {f"CP-ADJ-{index:02d}" for index in range(1, 7)}
        | {"CP-ELI-01", "CP-ELI-02", "CP-RES-01", "CP-RES-02", "CP-LIS-01"}
        | {f"CP-PRI-{index:02d}" for index in range(1, 5)}
        | {f"CP-ASG-{index:02d}" for index in range(1, 4)}
        | {f"CP-TAG-{index:02d}" for index in range(1, 5)}
        | {f"CP-ENL-{index:02d}" for index in range(1, 5)}
        | {"CP-HIS-01", "CP-HIS-02"}
        | {f"CP-FIL-{index:02d}" for index in range(1, 4)}
        | {f"CP-ORD-{index:02d}" for index in range(1, 3)}
        | {f"CP-ALT-{index:02d}" for index in range(1, 3)}
        | {f"CP-UI-{index:02d}" for index in range(1, 12)}
        | {f"CP-CB-{index:02d}" for index in range(1, 8)}
    )
    missing = expected - set(results)
    extra = set(results) - expected
    if missing:
        raise SystemExit(f"Faltan resultados: {', '.join(sorted(missing))}")
    if extra:
        raise SystemExit(f"Resultados inesperados: {', '.join(sorted(extra))}")

    text = ETAPA_5.read_text(encoding="utf-8")
    if INTRO_OLD in text:
        text = text.replace(INTRO_OLD, INTRO_NEW, 1)
    if COVERAGE_OLD in text:
        text = text.replace(COVERAGE_OLD, COVERAGE_NEW, 1)
    text = update_fiches(text, results)
    ETAPA_5.write_text(text, encoding="utf-8")

    passed = [item for item in results.values() if item["passed"]]
    summary = {
        "total": len(results),
        "aprobados": len(passed),
        "fallidos": len(results) - len(passed),
        "por_grupo": {
            group: {
                "total": len(ids),
                "aprobados": sum(1 for case_id in ids if results[case_id]["passed"]),
            }
            for group, ids in groups.items()
        },
        "casos": list(results.values()),
    }
    summary_path = EVIDENCE_DIR / "resumen_resultados.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Actualizado: {ETAPA_5}")
    print(
        f"Total: {summary['aprobados']}/{summary['total']} aprobados, "
        f"{summary['fallidos']} fallidos"
    )
    for group, data in summary["por_grupo"].items():
        print(f"  {group}: {data['aprobados']}/{data['total']}")
    return 0 if summary["fallidos"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
