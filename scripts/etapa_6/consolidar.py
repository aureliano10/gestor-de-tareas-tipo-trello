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
    "Esta etapa es de **diseño**. Los casos se documentan con todos sus campos, "
    "pero la ejecución y el registro de resultados corresponden a la Etapa 6. "
    "Por ese motivo, los campos `Resultado obtenido` y `Estado` se completan "
    "como pendientes."
)
INTRO_NEW = (
    "Esta etapa es de **diseño**. Los casos se documentan con todos sus campos. "
    "La ejecución y el registro de resultados se realizaron en la Etapa 6; por "
    "ese motivo, los campos `Resultado obtenido` y `Estado` reflejan los "
    "resultados de esa ejecución."
)

COVERAGE_OLD = (
    "La cobertura real se medirá durante la ejecución de las pruebas y las "
    "pruebas unitarias de la Etapa 8."
)
COVERAGE_NEW = (
    "La cobertura real se verificó durante la ejecución de la Etapa 6; las "
    "pruebas unitarias formales se incorporarán en la Etapa 8."
)

FICHE_UPDATES = {
    "CP-CB-01": [
        (
            '- Datos de entrada: "Tarea válida"; "     "; "a" repetido 101 veces.',
            '- Datos de entrada: "  Tarea válida  "; ""; "     "; "a" repetido '
            "101 veces.",
        ),
        (
            "- Resultado esperado: El primer dato devuelve \"Tarea válida\"; el "
            "segundo lanza un error de título vacío; el tercero lanza un error "
            "de longitud.",
            "- Resultado esperado: El primer dato devuelve \"Tarea válida\"; la "
            "cadena vacía y la de solo espacios lanzan error de título vacío; "
            "la de 101 caracteres lanza error de longitud.",
        ),
    ],
    "CP-CB-04": [
        (
            '- Datos de entrada: "     "; "a" repetido 101 veces; "Tarea '
            'válida"; "Tarea con error" con una función `onCreate` que rechaza.',
            '- Datos de entrada: ""; "     "; "a" repetido 101 veces; "Tarea '
            'válida"; "Tarea con error" con la API interceptada para responder '
            "HTTP 500.",
        ),
        (
            "- Precondiciones: Componente montado en un entorno de pruebas y "
            "función `onCreate` simulada.",
            "- Precondiciones: Aplicación completa en ejecución (backend y "
            "frontend); la petición POST se intercepta para simular un error "
            "de API.",
        ),
        (
            "- Procedimiento: Disparar el envío del formulario con cada dato, "
            "incluida una ejecución con `onCreate` rechazando, y observar el "
            "mensaje y la invocación de la función.",
            "- Procedimiento: Ejecutar el formulario real con cada dato, "
            "incluida una ejecución con la API interceptada para responder "
            "HTTP 500, y observar el mensaje y las peticiones emitidas.",
        ),
        (
            "- Resultado esperado: El título vacío muestra un error y no invoca "
            "la función; el de 101 caracteres muestra un error y no invoca; el "
            "válido invoca `onCreate` con el texto recortado y limpia el campo; "
            "si `onCreate` rechaza, se muestra el mensaje de error devuelto.",
            "- Resultado esperado: El título vacío muestra un error y no emite "
            "la petición; el de 101 caracteres muestra un error y no emite; el "
            "válido emite la petición y limpia el campo; si la API falla, se "
            "muestra el mensaje de error devuelto.",
        ),
        (
            "- Observaciones: El atributo `maxLength` limita el ingreso manual "
            "a 100; el caso de 101 y el error de API se prueban a nivel de la "
            "lógica del componente.",
            "- Observaciones: El atributo `maxLength` limita el ingreso manual "
            "a 100; el valor de 101 se carga programáticamente para ejercitar "
            "la rama de validación. Se ejecuta sobre la interfaz real en lugar "
            "de aislar el componente, cubriendo las mismas ramas de "
            "`handleSubmit`.",
        ),
    ],
    "CP-CB-05": [
        (
            "- Precondiciones: Columna con una tarea y función `onMove` simulada.",
            "- Precondiciones: Aplicación completa en ejecución y una tarea "
            "creada en la columna Pendiente.",
        ),
        (
            "- Procedimiento: Invocar `handleDrop` con cada combinación y "
            "registrar si se llama a `onMove`.",
            "- Procedimiento: Arrastrar la tarjeta con eventos de arrastre "
            "reales hacia la misma columna, hacia otra columna y soltar "
            "identificadores inválidos; registrar las peticiones PATCH.",
        ),
        (
            "- Resultado esperado: La misma columna no invoca `onMove`; la "
            "columna distinta invoca `onMove` con el id y el estado correctos; "
            "el identificador inválido no invoca.",
            "- Resultado esperado: La misma columna no emite PATCH; la columna "
            "distinta emite un PATCH con el id y el estado correctos; el "
            "identificador inválido no emite PATCH y la tarjeta no cambia de "
            "columna.",
        ),
        (
            "- Observaciones: Cubre los resultados de `Number.isInteger(taskId) "
            "&& taskId > 0 && !alreadyInColumn`.",
            "- Observaciones: Cubre los resultados de `Number.isInteger(taskId) "
            "&& taskId > 0 && !alreadyInColumn`. Se ejecuta sobre la interfaz "
            "real en lugar de aislar el componente, cubriendo las mismas "
            "condiciones.",
        ),
    ],
}


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
    expected = {
        f"CP-CRE-{index:02d}" for index in range(1, 9)
    } | {
        f"CP-MOV-{index:02d}" for index in range(1, 5)
    } | {
        f"CP-ELI-{index:02d}" for index in range(1, 3)
    } | {
        "CP-LIS-01",
        "CP-UI-01",
        "CP-UI-02",
        "CP-UI-03",
        "CP-UI-04",
        "CP-UI-05",
        "CP-CB-01",
        "CP-CB-02",
        "CP-CB-03",
        "CP-CB-04",
        "CP-CB-05",
    }
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
