# ACTIVIDAD INTEGRADORA - VERIFICACIÓN Y VALIDACIÓN

**Materia:** Verificación y Validación de software
**Curso:** Tercer Año "TSDS"
**Integrantes:** Aureliano Eichhorn, Nicolás Delfino
**Fecha:** 01/11/2026

# Etapa 14 - Revisión de artefactos no código

## Objetivo de la etapa

Además del programa, revisar al menos un artefacto **no relacionado directamente con el código** (documentación, manual de usuario, ayuda del sistema, instrucciones de instalación o material de capacitación), y registrar los problemas encontrados. El objetivo de esta revisión es comprobar que la documentación del proyecto describa de forma **veraz, completa y consistente** el comportamiento y la estructura reales del sistema, y corregir las diferencias detectadas.

## Artefactos seleccionados y por qué

Se eligieron tres artefactos de la categoría **instrucciones de instalación / documentación** por ser los que un tercero usa para instalar, ejecutar y probar el sistema desde cero:

| Artefacto | Tipo | Por qué se revisa |
|-----------|------|-------------------|
| `README.md` | Documentación general + instrucciones de instalación | Es la puerta de entrada al proyecto: describe funcionalidades, estructura, instalación y API. Un error acá afecta a cualquiera que intente reproducir el trabajo. |
| `COMANDOS_BACKEND.md` | Instrucciones de instalación/ejecución | Es la guía específica para levantar y operar el backend; debe coincidir con `README.md` y con el script `backend/run_backend.sh`. |
| `backend/requirements-dev.txt` | Lista de dependencias de desarrollo | Es la contraparte concreta de las instrucciones de instalación: si no declara los paquetes que las pruebas necesitan, los pasos documentados no son reproducibles. |

No se modificaron los documentos de etapas (`docs/Etapa_*.md`) porque ya habían sido revisados y versionados en sus entregas, ni los artefactos de código, que quedan fuera del alcance de esta etapa.

## Metodología

Se aplicó una **revisión de escritorio (desk check) con inspección cruzada**, del tipo usado en la revisión de artefactos de documentación:

1. **Inventario:** se listaron los artefactos no-código del repositorio (README, COMANDOS_BACKEND, carpeta `docs/`, archivos de dependencias).
2. **Lectura y extracción de afirmaciones:** se anotó cada afirmación verificable de los artefactos (comandos, rutas, puertos, límites, estructura de carpetas, pasos de instalación).
3. **Contraste contra el sistema real:** cada afirmación se comparó con el código y la configuración efectivos (`backend/app/schemas.py`, `backend/app/database.py`, `backend/app/repository.py`, `backend/app/routers/`, `backend/run_backend.sh`, `frontend/vite.config.js`, `ruff.toml`) y con la ejecución real de los comandos.
4. **Contraste cruzado entre artefactos:** se comparó `README.md` contra `COMANDOS_BACKEND.md` para detectar inconsistencias.
5. **Registro y corrección:** cada diferencia se registró como problema (ID `PRB-NN`) con severidad, y se aplicó la corrección sobre el artefacto de origen.

La revisión se enfocó en cuatro clases de defectos propuestas en la consigna: comandos desactualizados o incompletos, pasos faltantes, inconsistencias entre artefactos, y faltas de ortografía o redacción confusa.

## Entorno de ejecución

| Componente | Versión o configuración |
|------------|--------------------------|
| Sistema operativo | Linux Mint 22.3 (kernel 6.8.0-137-generic) |
| Python | 3.12.3 |
| pytest | 9.2.0 |
| httpx | 0.28.1 |
| Playwright | 1.64.1 |
| ruff | 0.17.3 |
| Node.js | v24.14.1 |
| Versión de la API | 1.0.0 (FastAPI 0.136.3) |

## Problemas encontrados

| ID | Artefacto | Ubicación | Problema | Severidad | Corrección aplicada | Estado |
|----|-----------|-----------|----------|-----------|---------------------|--------|
| PRB-01 | `README.md` | Sección "Análisis estático" | El comando de lint documentado (`ruff check backend`) no cubre `scripts/`, que sí contiene código Python del proyecto. Comando incompleto. | Media | Se cambió a `ruff check backend scripts`. | Corregido |
| PRB-02 | `README.md` | Sección "Estructura del proyecto" | La estructura solo listaba `scripts/etapa_6/`, pero el repositorio también tiene `scripts/etapa_8/` y `scripts/etapa_9/`. Estructura desactualizada. | Baja | Se agregaron las dos carpetas faltantes con su descripción. | Corregido |
| PRB-03 | `README.md` | Documento completo | No había ninguna instrucción para ejecutar las pruebas automatizadas (pytest, runners de Playwright/httpx). Paso faltante. | Alta | Se agregó la sección "Pruebas". | Corregido |
| PRB-04 | `README.md` | Sección "Instalación y ejecución → 1. Backend" | Indicaba levantar el backend con `uvicorn app.main:app --reload` y no mencionaba `backend/run_backend.sh`, que `COMANDOS_BACKEND.md` presenta como forma recomendada. Inconsistencia entre artefactos. | Media | Se alineó con el script del proyecto y se aclaró la forma manual. | Corregido |
| PRB-05 | `COMANDOS_BACKEND.md` | Documento completo | No explicaba cómo instalar las dependencias de desarrollo ni cómo ejecutar las pruebas. Paso faltante. | Media | Se agregó la sección "5. Ejecutar las pruebas" y una nota sobre `requirements-dev.txt`. | Corregido |
| PRB-06 | `backend/requirements-dev.txt` | Archivo completo | Las dependencias de pruebas (pytest, httpx y playwright) no estaban declaradas en ningún `requirements`, aunque las pruebas las usan y estaban instaladas en `.venv`. En una clonación limpia los pasos de prueba documentados fallarían. | Alta | Se agregaron `pytest==9.2.0`, `httpx==0.28.1` y `playwright==1.64.1`. | Corregido |
| PRB-07 | `COMANDOS_BACKEND.md` | Sección "Notas" | La forma verbal "no te olvidés" no es la estándar del imperativo negativo en español rioplatense. Falta de ortografía. | Baja | Se reemplazó por "no te olvides". | Corregido |

Resumen: **7 problemas**, todos corregidos (2 de severidad Alta, 3 Media y 2 Baja).

## Fragmentos antes/después

### PRB-01 – Comando de lint incompleto (`README.md`)

**Antes**
```bash
pip install -r backend/requirements-dev.txt
ruff check backend
python -m compileall backend/app
```

**Después**
```bash
pip install -r backend/requirements-dev.txt
ruff check backend scripts
python -m compileall backend/app
```

### PRB-02 – Estructura desactualizada (`README.md`)

**Antes**
```text
docs/                      # Documentación de cada etapa
scripts/etapa_6/           # Scripts de ejecución de los casos de prueba
```

**Después**
```text
docs/                      # Documentación de cada etapa
scripts/etapa_6/           # Scripts de ejecución de los casos de prueba de sistema
scripts/etapa_8/           # Runner de las pruebas unitarias (pytest)
scripts/etapa_9/           # Runner de las pruebas de integración (pytest)
```

### PRB-03 – Falta de instrucciones de prueba (`README.md`)

**Antes:** el README terminaba la parte técnica en "Análisis estático" y pasaba directo a "Endpoints de la API"; no había forma de saber cómo correr las pruebas.

**Después:** se agregó la sección "Pruebas":

```markdown
## Pruebas

Las dependencias de lint y de pruebas (pytest, httpx y Playwright) se instalan con el archivo de desarrollo...

    pip install -r backend/requirements-dev.txt

Pruebas de backend (unitarias e integración) con pytest, sin necesidad de levantar el servidor:

    .venv/bin/python -m pytest backend/tests -v

Casos de sistema (API con httpx, interfaz con Playwright y caja blanca)...

    .venv/bin/python scripts/etapa_6/ejecutar_api.py
    .venv/bin/python scripts/etapa_6/ejecutar_ui.py
    .venv/bin/python scripts/etapa_6/ejecutar_caja_blanca.py
```

### PRB-04 – Inconsistencia de arranque del backend (`README.md`)

**Antes**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload
```

**Después**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
bash backend/run_backend.sh
```

(y, como alternativa manual, `cd backend && ../.venv/bin/python -m uvicorn app.main:app --reload`).

### PRB-05 – Faltaba el apartado de pruebas (`COMANDOS_BACKEND.md`)

**Antes:** el documento terminaba en "4. Detener el servidor" y seguía con "Notas".

**Después:** se incorporó la sección "5. Ejecutar las pruebas":

```markdown
## 5. Ejecutar las pruebas

    .venv/bin/pip install -r backend/requirements-dev.txt
    .venv/bin/python -m pytest backend/tests -v

    .venv/bin/python scripts/etapa_6/ejecutar_api.py
    .venv/bin/python scripts/etapa_6/ejecutar_ui.py
    .venv/bin/python scripts/etapa_6/ejecutar_caja_blanca.py
```

### PRB-06 – Dependencias de prueba no declaradas (`backend/requirements-dev.txt`)

**Antes**
```text
ruff==0.17.3
```

**Después**
```text
ruff==0.17.3
pytest==9.2.0
httpx==0.28.1
playwright==1.64.1
```

### PRB-07 – Ortografía en las notas (`COMANDOS_BACKEND.md`)

**Antes:** `Si usás el comando manual, no te olvidés del cd backend.`
**Después:** `Si usás el comando manual, no te olvides del cd backend.`

## Verificación de las correcciones

Las correcciones se comprobaron ejecutando los comandos documentados:

| Comando | Resultado |
|---------|-----------|
| `.venv/bin/pip install -r backend/requirements-dev.txt` | Todas las dependencias ya satisfechas (instalación exitosa). |
| `.venv/bin/ruff check backend scripts` | `All checks passed!` |
| `.venv/bin/python -m pytest backend/tests -v` | `25 passed, 1 warning` |

## Conclusión

Se revisaron tres artefactos no-código (`README.md`, `COMANDOS_BACKEND.md` y `backend/requirements-dev.txt`) mediante inspección cruzada contra el sistema real. Se detectaron y corrigieron **7 problemas**: dos de severidad alta (falta de instrucciones de prueba y dependencias de prueba sin declarar), tres de severidad media (comando de lint incompleto, inconsistencia del arranque del backend y falta del apartado de pruebas en el instructivo) y dos de severidad baja (estructura desactualizada y una falta de ortografía). Tras las correcciones, los artefactos describen de forma consistente cómo instalar, ejecutar y probar el sistema, y los comandos documentados se validaron con una ejecución real. No se modificó ningún artefacto de código.

## Evidencias

| Evidencia | Ubicación |
|-----------|-----------|
| Registro de problemas (JSON) | `docs/evidencias/etapa_14/problemas_no_codigo.json` |
| Diff de los artefactos corregidos | `docs/evidencias/etapa_14/diff_artefactos.txt` |
| Instalación de dependencias de desarrollo | `docs/evidencias/etapa_14/pip_install_dev.txt` |
| Análisis estático (`ruff check backend scripts`) | `docs/evidencias/etapa_14/ruff_check.txt` |
| Pruebas de backend (`pytest backend/tests -v`) | `docs/evidencias/etapa_14/pytest_tests.txt` |

## Reproducibilidad

1. **Lint de los artefactos de código:** desde la raíz, `.venv/bin/ruff check backend scripts`.
2. **Instalación de dependencias de prueba:** `.venv/bin/pip install -r backend/requirements-dev.txt`.
3. **Pruebas de backend:** `.venv/bin/python -m pytest backend/tests -v`.
4. **Diff de los artefactos no-código revisados:** `git diff -- README.md COMANDOS_BACKEND.md backend/requirements-dev.txt`.
