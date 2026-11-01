# Auditoría de Frontend — Tablero Kanban (React 19 + Vite)

## 1. Introducción y alcance

Este informe documenta una **auditoría de frontend** de la aplicación *Tablero de Tareas* (cliente React 19 + Vite, con backend FastAPI) del proyecto *Actividad Integradora* de Verificación y Validación de Software. El objetivo es evaluar la calidad del cliente en cuatro dimensiones —accesibilidad, rendimiento/bundle, calidad de código React y UX/consistencia visual— y dejar hallazgos **reales, verificables y accionables**.

**Alcance revisado (solo frontend, sin modificar código de la aplicación):**

- `frontend/src/App.jsx`, `frontend/src/api.js`, `frontend/src/format.js`, `frontend/src/main.jsx`
- `frontend/src/components/`: `Board.jsx`, `Column.jsx`, `ConfirmDialog.jsx`, `DueBadge.jsx`, `TaskCard.jsx`, `TaskDetailModal.jsx`, `TaskFields.jsx`, `TaskForm.jsx`, `Toast.jsx`
- `frontend/src/styles/app.css`
- Configuración: `frontend/package.json`, `frontend/vite.config.js`, `frontend/eslint.config.js`, `frontend/index.html`

**Fuera de alcance:** el backend (`backend/`), la lógica de negocio del servidor y las pruebas automatizadas. Esta auditoría es estática (lectura de código) más la ejecución real de `npm run build` y `npm run lint`; no incluye pruebas manuales con lector de pantalla.

**Restricción respetada:** no se modificó ningún archivo `.jsx`, `.js` ni `.css` de la aplicación. Todos los artefactos producidos son de documentación/evidencia.

## 2. Metodología

Se realizó una revisión estática archivo por archivo del código fuente, complementada con la ejecución real del build de producción, del linter y con el cálculo programático de ratios de contraste WCAG a partir de los valores hexadecimales definidos en `app.css`.

### 2.1 Herramientas y comandos ejecutados

| Comando | Directorio | Resultado |
|---|---|---|
| `npm run build` | `frontend/` | Exitoso (código de salida 0), sin advertencias de Vite |
| `npm run lint` | `frontend/` | Exitoso (código de salida 0), sin errores ni advertencias |
| Cálculo de contraste (script Python sobre los hex de `app.css`) | raíz del repo | Ver tabla de la sección 3.3 |

La salida cruda de ambos comandos quedó guardada como evidencia en `docs/evidencias/auditoria_frontend/`.

### 2.2 Resultado real de `npm run build`

```
> kanban-frontend@1.0.0 build
> vite build

vite v8.3.5 building client environment for production...
transforming...
✓ 27 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.40 kB │ gzip:  0.26 kB
dist/assets/index-BV7iYHSe.css   22.72 kB │ gzip:  4.96 kB
dist/assets/index-VEcTaZot.js   253.73 kB │ gzip: 77.25 kB

✓ built in 253ms
```

**Lectura:** un único chunk JS de **253.73 kB** (77.25 kB gzip) y un CSS de **22.72 kB** (4.96 kB gzip). Vite **no emitió advertencias** (el chunk queda por debajo del umbral por defecto de 500 kB), por lo que el proyecto compila limpio. No hay `dist/` versionado.

### 2.3 Resultado real de `npm run lint`

```
> kanban-frontend@1.0.0 lint
> eslint .

(sin salida — 0 problemas)
```

**Lectura:** ESLint (config *flat* con `eslint-plugin-react` y `eslint-plugin-react-hooks`, incluyendo `react-hooks/exhaustive-deps` en modo `warn`) **no reporta ningún error ni advertencia**. En particular, ningún `useEffect` dispara la advertencia de dependencias faltantes. Es un punto a favor de la calidad del código.

### 2.4 Cálculo de contraste

Se implementó un cálculo WCAG 2.x estándar (luminancia relativa con corrección gamma y ratio `(L1+0.05)/(L2+0.05)`). Para los colores con transparencia (`rgba`) y `color-mix(in srgb, ...)` se calculó primero el color compuesto sobre el fondo real (composición alfa y mezcla en espacio sRGB, respectivamente). Umbrales aplicados: **4.5:1** para texto normal, **3:1** para texto grande y para componentes/indicadores no textuales (WCAG 1.4.3, 1.4.11 y 2.4.11). Evidencia: `docs/evidencias/auditoria_frontend/contraste_wcag.txt`.

## 3. Dimensión 1 — Accesibilidad (a11y)

### 3.1 Aspectos bien resueltos (con evidencia)

La base semántica es sólida y hay una conciencia clara de accesibilidad en varias partes:

- **HTML semántico correcto en el tablero.** `Board.jsx` usa `<section aria-label="Tablero Kanban">`; `Column.jsx` usa `<header>` con `<h2>`; cada tarjeta es un `<article>`; los paneles del modal usan `<section>` con `<h3>`. No hay `div` clickeables salvo donde se documenta abajo.
- **Formularios etiquetados de verdad.** `TaskFields.jsx` genera `id` con `idPrefix` y los asocia con `<label htmlFor={...}>` (líneas 36, 50, 64, 77, 94). En la barra, los `<select>` van envueltos por su `<label className="filter">` (asociación implícita válida). El buscador usa `aria-label="Buscar tareas"`.
- **ARIA en modales y mensajes.** El modal de detalle declara `role="dialog"`, `aria-modal="true"` y `aria-labelledby="task-detail-title"`; el diálogo de confirmación declara `role="alertdialog"` con `aria-labelledby`/`aria-describedby`. Los errores usan `role="alert"` (p. ej. `data-testid="app-error"`, `edit-error`, `link-error`). El aviso (`Toast.jsx`) usa `role="status"`.
- **Etiquetas accesibles en botones icónicos.** Los botones de borrar subtarea/enlace/adjunto usan `aria-label` descriptivo y contextual (p. ej. `aria-label={`Quitar enlace ${link.url}`}`).
- **Escape funciona en modales**, `prefers-reduced-motion` está contemplado (`app.css` 1583-1588) y el punto del historial es decorativo con `aria-hidden="true"`.
- **Sin imágenes:** no hay elementos `<img>` ni `<svg>` en todo `src/`, así que no hay textos alternativos pendientes.

### 3.2 Hallazgos de accesibilidad

**AUD-01 (Alta) — Sin trampa de foco ni gestión de foco en los modales.**
Ni `TaskDetailModal` ni `ConfirmDialog` atrapan el foco (Tab escapa al contenido del fondo) ni mueven el foco al abrir. `TaskDetailModal` no tiene ninguna referencia de foco; `ConfirmDialog` sí enfoca el botón de confirmar (`confirmRef.current?.focus()`, línea 13) pero igual permite salir con Tab y no restaura el foco al disparador al cerrar. WCAG 2.4.3 (orden del foco). Impacto: usuarios de teclado/lector de pantalla pueden "perderse" detrás del modal.

**AUD-02 (Alta) — Mover tareas entre columnas solo es posible por *drag & drop*, sin alternativa de teclado.**
El único mecanismo para cambiar de estado es HTML5 drag&drop (`Column.jsx` `handleDrop`, líneas 54-64; `TaskCard.jsx` `draggable="true"`). El modal de detalle muestra el estado pero no ofrece un control para cambiarlo. WCAG 2.1.1 (teclado). Impacto: un usuario que no usa mouse no puede completar la tarea central del producto.

**AUD-03 (Alta) — El input de archivo del modal no es alcanzable por teclado.**
En `TaskDetailModal.jsx` (líneas 550-557) el `<input type="file">` va dentro de un `<label className="upload">`, pero `app.css` lo oculta con `display: none` (líneas 1217-1219). Un elemento con `display:none` no recibe foco, y el `<label>` no es enfocable por sí mismo. Resultado: **no hay forma de adjuntar un archivo en el modal usando solo el teclado**. (En `TaskForm` sí es alcanzable porque usa `.extras__file`, que es visible.)

**AUD-04 (Alta) — Contraste insuficiente en los botones en modo oscuro.**
El gradiente de `.btn` usa `--primary` → `--primary-dark` con texto blanco. En modo oscuro `--primary: #8b83ff` y `--primary-dark: #a49cff`, y el blanco sobre esos fondos da **3.09:1** y **2.39:1** respectivamente, muy por debajo de 4.5:1. Afecta a todos los botones primarios del sistema (Agregar tarea, Guardar, Agregar, etc.). WCAG 1.4.3.

**AUD-05 (Alta) — El aviso de error (`.alert`) es ilegible en modo oscuro.**
`app.css` redefine `--danger` y `--danger-soft` en el bloque oscuro (líneas 62-63), pero **no redefine `--danger-dark`**, que sigue valiendo `#c2262b` (rojo oscuro). `.alert` usa `color: var(--danger-dark)` sobre `background: var(--danger-soft)` compuesto sobre el fondo oscuro → **2.71:1**. WCAG 1.4.3. Afecta a todos los errores globales del tablero.

**AUD-06 (Media) — Contraste de `--muted` insuficiente en modo claro.**
`--muted: #7a8199` se usa para muchísimos textos de apoyo: etiquetas de campo (`.field label`), descripciones de tarjeta (`.task__description`), ayuda (`.hint`), resumen del contador (`.toolbar__summary`), `Cargando tareas...`, encabezados de panel (`.panel__header h3`) y fechas del historial. Ratios calculados: **3.87:1** sobre superficie blanca, **3.42:1** sobre el fondo de página, **3.64:1** sobre `--surface-2` y **3.37:1** sobre `--surface-3`. Todos por debajo de 4.5:1. WCAG 1.4.3.

**AUD-07 (Media) — El indicador de foco tiene contraste muy bajo.**
`*:focus-visible` aplica `outline: none` y solo deja `box-shadow: var(--ring)`, donde `--ring` es `0 0 0 3px var(--primary-soft)` y `--primary-soft` es `rgba(91,83,232,0.12)`. Compuesto sobre blanco el anillo da **1.19:1** (y **1.27:1** en oscuro), muy por debajo del 3:1 exigido para el indicador de foco (WCAG 1.4.11 / 2.4.11). Impacto: usuarios de teclado con baja visión apenas distinguen dónde está el foco.

**AUD-08 (Media) — Bordes de controles con contraste insuficiente.**
El borde de inputs/selects es `--border-strong: #cfd5e8` sobre el fondo del input `--surface-2: #f6f8fd` → **1.38:1** (y **1.46:1** sobre blanco). En oscuro, `#3a4270` sobre `#1c2137` → **1.66:1**. WCAG 1.4.11 (contraste de componentes no textuales): el límite de un control debe ser perceptible, umbral 3:1.

**AUD-09 (Media) — La tarjeta es clickeable pero no operable por teclado.**
`TaskCard.jsx` es un `<article>` con `onClick={() => onOpen(task.id)}` (líneas 18-26) sin `role`, `tabIndex` ni `onKeyDown`. Un `<article>` no es enfocable. Se mitiga parcialmente porque existe un `<button>Abrir</button>` interno (líneas 81-90), pero la affordance visual (`cursor: grab` + toda la tarjeta clickeable) no se corresponde con la operabilidad por teclado.

**AUD-10 (Media) — Escape cierra el modal y descarta la edición en curso sin aviso.**
`TaskDetailModal.jsx` (líneas 66-74) registra un `keydown` global que llama a `onClose()` ante Escape, sin verificar si `editing` está activo. Un usuario que está editando y presiona Escape (o intenta cerrar un autocompletado) pierde los cambios sin confirmación.

**AUD-11 (Media) — Badges de prioridad por debajo del umbral en modo claro.**
`.badge--priority-alta` (**4.25:1**) y `.badge--priority-media` (**4.28:1**) quedan apenas por debajo de 4.5:1 para texto pequeño (0.7rem ≈ 11px). Los colores se obtienen con `color-mix` sobre `--danger` y `--progress`.

**AUD-12 (Media) — La carga inicial no se anuncia a lectores de pantalla.**
`App.jsx` renderiza `<p className="loading">Cargando tareas...</p>` (líneas 261-262) sin `aria-live` ni `role="status"`. Un lector de pantalla no anuncia el inicio ni el fin de la carga.

**AUD-13 (Baja) — Overlay con `role="presentation"` y `onClick`.**
Tanto `TaskDetailModal` como `ConfirmDialog` envuelven el diálogo en `<div className="overlay" onClick={...} role="presentation">`. El `role="presentation"` elimina la semántica, pero el `onClick` (cerrar al tocar el fondo) no tiene equivalente de teclado. No es bloqueante (Escape funciona), pero es una inconsistencia.

**AUD-14 (Baja) — Contraste bajo del aviso en modo oscuro.**
En oscuro el `.toast` invierte a fondo claro (`background: var(--text)`), y entonces: la acción "Deshacer" (`color: var(--primary) #8b83ff`) da **2.74:1** y el botón cerrar (`color: var(--muted)`) **2.56:1**.

### 3.3 Tabla de contraste WCAG calculado

**Modo claro**

| Par texto/fondo | Uso principal | Ratio | ¿Cumple 4.5:1? |
|---|---|---|---|
| `#14182b` / `#ffffff` | texto principal | 17.57:1 | Sí |
| `#4a5169` / `#ffffff` | texto suave | 7.86:1 | Sí |
| `#7a8199` / `#ffffff` | descripción, etiquetas, hints | 3.87:1 | **No** |
| `#7a8199` / `#eef1f9` | subtítulo del header | 3.42:1 | **No** |
| `#7a8199` / `#f6f8fd` | h3 de panel, fechas | 3.64:1 | **No** |
| `#7a8199` / `#eceffa` | contadores | 3.37:1 | **No** |
| `#443ccd` / `#ffffff` | enlaces, botón fantasma | 7.57:1 | Sí |
| `#443ccd` / primary-soft | chips, tags | 6.38:1 | Sí |
| `#ffffff` / `#5b53e8` | botón (gradiente, arriba) | 5.46:1 | Sí |
| `#ffffff` / `#443ccd` | botón (gradiente, abajo) | 7.57:1 | Sí |
| `#e5484d` / `#f6f8fd` | "· vencida" en header modal | 3.68:1 | **No** |
| `#c2262b` / `#fdeeee` | `.alert`, badge vencida | 5.17:1 | Sí |
| `#b45309` / `#fff4e5` | badge vence hoy/ pronto | 4.62:1 | Sí (justo) |
| `#067647` / `#e7f8ef` | badge completo | 5.17:1 | Sí |
| `#6435c9` / `#f0edff` | badge archivos | 6.31:1 | Sí |
| prioridad Alta (compuesto) | badge prioridad | 4.25:1 | **No** |
| prioridad Media (compuesto) | badge prioridad | 4.28:1 | **No** |
| anillo de foco (primary-soft) | foco visible | 1.19:1 | **No** (umbral 3:1) |
| borde `#cfd5e8` / `#f6f8fd` | borde de input | 1.38:1 | **No** (umbral 3:1) |

**Modo oscuro**

| Par texto/fondo | Uso principal | Ratio | ¿Cumple? |
|---|---|---|---|
| `#eef1fb` / `#161a2e` | texto principal | 15.24:1 | Sí |
| `#c3c9e2` / `#161a2e` | texto suave | 10.46:1 | Sí |
| `#8f97b6` / `#161a2e` | descripción, hints | 5.95:1 | Sí |
| `#ffffff` / `#8b83ff` | **botón (gradiente, arriba)** | 3.09:1 | **No** |
| `#ffffff` / `#a49cff` | **botón (gradiente, abajo)** | 2.39:1 | **No** |
| `#c2262b` / fondo alerta oscuro | **`.alert`** | 2.71:1 | **No** |
| `#8b83ff` / `#eef1fb` | acción del toast | 2.74:1 | **No** |
| `#8f97b6` / `#eef1fb` | cerrar toast | 2.56:1 | **No** |
| anillo de foco (compuesto) | foco visible | 1.27:1 | **No** |
| borde `#3a4270` / `#161a2e` | borde de control | 1.80:1 | **No** |
| badges dark (today/complete/files/prioridad) | varios | 7.08–7.90:1 | Sí |

## 4. Dimensión 2 — Rendimiento y bundle

**Build real:** 253.73 kB JS (77.25 kB gzip) + 22.72 kB CSS (4.96 kB gzip), 27 módulos, en 253 ms, **sin advertencias**. Puntos a favor: **no hay imágenes ni íconos como archivos** (todos los íconos son glifos de texto como `×` y `▸`), y la tipografía usa la pila del sistema (`--font-sans` incluye `"Inter"` primero pero **no hay `@font-face`**, por lo que no se descarga ninguna fuente). El peso del bundle se explica casi enteramente por React 19 + ReactDOM.

**AUD-15 (Media) — Re-render completo del tablero en cada tecla de búsqueda.**
`App.jsx` tiene el estado `query` y lo actualiza en cada pulsación (`onChange={(event) => setQuery(event.target.value)}`, línea 199). Ese cambio de estado re-renderiza `App` completo, y como `Board`, `Column` y `TaskCard` no están memoizados (`React.memo` no se usa en ningún lado), se vuelven a renderizar los tres columnas y **todas** las tarjetas por cada letra tipeada, aunque `tasks` no cambió (el fetch recién ocurre tras el *debounce* de 300 ms). Además, `Board.jsx` calcula `tasks.filter((task) => task.status === status)` en cada render (línea 19) creando tres arreglos nuevos. Recomendación: `React.memo` en `TaskCard`/`Column`, memoizar el filtrado y/o aislar el input en un componente controlado local.

**AUD-16 (Media) — Doble petición a `/tags` al iniciar.**
`App.load` pide las etiquetas con `Promise.all([getTasks(filters), getTags()])` (`App.jsx` línea 71) y, por separado, `TaskForm` las vuelve a pedir en su propio `useEffect` (`TaskForm.jsx` líneas 79-91). La misma información se descarga dos veces en el arranque (y en cada recarga del tablero se repite la de `App`).

**AUD-17 (Media) — Sin *code splitting* ni *lazy loading*.**
No hay `React.lazy`, imports dinámicos ni `Suspense` en el proyecto. `TaskDetailModal` (el componente más grande del cliente), `ConfirmDialog` y `Toast` se empaquetan siempre en el bundle inicial aunque solo se muestren bajo interacción. El ahorro real es acotado (React domina el peso), pero es una oportunidad concreta y de bajo riesgo.

**AUD-18 (Baja) — Un único chunk, sin separación de dependencias.**
`vite.config.js` no define `build.rollupOptions.manualChunks`, así que React/ReactDOM van en el mismo chunk que el código de la app, impidiendo el cacheo diferido del *vendor* entre despliegues.

## 5. Dimensión 3 — Calidad de código React

**`npm run lint` limpio (0 problemas)**, incluyendo `react-hooks/exhaustive-deps`. Revisados hooks, estado y efectos: no se encontraron dependencias incorrectas ni claves `key` duplicadas en las listas principales (`TaskCard` usa `key={task.id}`, subtareas `key={subtask.id}`, actividad `key={entry.id}`). La lógica de fechas está bien extraída en `format.js` (`daysUntil`, `dueInfo`, `formatDate`, `todayISO`), lo que aleja el cálculo de prioridades/vencimientos de los componentes.

**AUD-19 (Media) — Condición de carrera en la carga por filtros.**
`App.jsx` dispara `load(params)` en cada cambio de `params` (efecto de líneas 84-86) y `load` no usa `AbortController` ni guarda un identificador de petición. Si el usuario cambia filtros/orden rápido, la respuesta de una consulta anterior puede llegar después y **sobrescribir** `tasks` (y `loading`) con datos obsoletos. El *debounce* de la búsqueda reduce pero no elimina el problema.

**AUD-20 (Media) — Duplicación de la validación de enlaces y sus constantes.**
`TaskForm.jsx` (constantes 21-23 y `addLink` 173-206) y `TaskDetailModal.jsx` (constantes 13-15 y `handleAddLink` 162-202) repiten prácticamente el mismo bloque de validación (URL vacía, `http(s)`, largo de URL, largo de nombre, duplicado, máximo) y redefinen `MAX_LINKS`, `MAX_LINK_URL_LENGTH` y `MAX_LINK_LABEL_LENGTH`. Es duplicación de reglas de negocio que puede desincronizarse.

**AUD-21 (Media) — `TaskDetailModal` es un componente sobredimensionado.**
El archivo tiene ~617 líneas y una única función componente que maneja, a la vez: vista de detalle, edición de campos, alta/borrado/toggle de subtareas, alta/borrado de enlaces, subida/borrado de adjuntos y render del historial. Concentra demasiadas responsabilidades y mucho estado local (10 `useState`). Conviene extraer paneles (Checklist, Enlaces, Adjuntos, Historial) como componentes independientes.

**AUD-22 (Media) — `Promise.all` acopla el fallo de `/tags` al tablero.**
En `App.load` (línea 71), si `getTags()` falla pero `getTasks()` funciona, el `Promise.all` rechaza y se descarta la lista de tareas válida, mostrando el error global. La carga de tareas no debería depender del éxito de la carga de etiquetas.

**AUD-23 (Baja) — Rama de compatibilidad muerta en `getTasks`.**
`api.js` (líneas 38-39) acepta `typeof options === "boolean"`, pero `App` siempre pasa un objeto. Código legacy sin uso.

**AUD-24 (Baja) — Claves de lista basadas en índice en los borradores.**
`TaskForm.jsx` usa `key={`${title}-${index}`}` (líneas 387, 455, 532) combinando texto + índice para subtareas, enlaces y archivos del formulario. Al eliminar un ítem del medio, React puede reutilizar incorrectamente el nodo/DOM del ítem anterior (no hay `id` estable en los borradores).

**AUD-25 (Baja) — No hay *Error Boundary*.**
Si un componente lanza una excepción durante el render, toda la aplicación queda en blanco (no hay `componentDidCatch`/`ErrorBoundary` ni fallback). Es un riesgo de robustez más que un bug actual.

**AUD-26 (Baja) — Lógica del *slug* de prioridad duplicada.**
`TaskCard.jsx` (línea 35) y `TaskDetailModal.jsx` (línea 251) calculan por separado `task.priority.toLowerCase()` para armar la clase `badge--priority-*`. Es una micro-duplicación que debería resolverse con un helper.

**AUD-27 (Baja) — Handlers no memoizados pasados a los hijos.**
`App.jsx` define `handleCreate`, `handleUpdate`, `handleMove`, `handleAddSubtask`, etc. como funciones nuevas en cada render (líneas 130-141) y `TaskForm` recibe `onCreate`/`onUpload`; junto con los `onClick={() => ...}` inline de `TaskCard`, esto invalida cualquier intento de memoización (se relaciona con AUD-15).

**AUD-28 (Baja) — Mensajes de error de red en crudo.**
`api.js` no envuelve `fetch`: si falla la red, el error nativo (`TypeError: Failed to fetch`) se propaga y `App` lo muestra tal cual en el banner (`setError(err.message)`), sin un mensaje amigable en español.

## 6. Dimensión 4 — UX y consistencia visual

**Puntos a favor:** existen estados vacíos para todas las columnas (`column__empty` con hints específicos por estado) y para cada panel del detalle ("Todavía no hay subtareas.", "Sin enlaces.", "Sin archivos adjuntos.", "Sin actividad registrada."). El diseño es responsive con media queries en 720px y 860px (el tablero pasa de 3 a 1 columna; `.fields` y `.link-row` también colapsan). Hay tokens de color/radio/sombra definidos en `:root` y un modo oscuro completo vía `prefers-color-scheme`.

**AUD-29 (Media) — El *drag & drop* no funciona en dispositivos táctiles.**
El arrastre de tarjetas usa la API HTML5 de *drag and drop* (`TaskCard.jsx` `draggable`, `Column.jsx` `onDrop`), que **no tiene soporte táctil**. Como además no existe un control alternativo para cambiar de estado (ver AUD-02), en un celular/tablet **es imposible mover tareas entre columnas**.

**AUD-30 (Media) — El estado de carga reemplaza el tablero y provoca salto de layout.**
`App.jsx` alterna entre `<p className="loading">Cargando tareas...</p>` y `<Board .../>` (líneas 261-270). En cada cambio de filtro (`load` vuelve a `loading = true`), el tablero desaparece y reaparece, generando un salto visual y sin *skeleton*/spinner. El refresco silencioso (`refresh`) no muestra ningún indicador.

**AUD-31 (Media) — Acciones secundarias sin estado de "enviando"/deshabilitado.**
Solo el submit de creación (`submitting`) y el guardado de edición (`saving`) deshabilitan el botón. El alta de subtarea, el alta de enlace, el adjuntar archivo y el borrar adjunto/subtarea no muestran progreso ni se deshabilitan, habilitando dobles envíos por clics repetidos (p. ej. `data-testid="subtask-add"`, `link-add`).

**AUD-32 (Media) — Áreas táctiles menores a 44×44 px.**
Varios controles quedan por debajo del mínimo táctil recomendado (44×44 px; WCAG 2.5.8 pide 24×24 como piso): `.icon-button` mide 1.7rem ≈ **27.2 px**, `.chip__remove` 1.1rem ≈ **17.6 px**, `.toast__close` 1.6rem ≈ **25.6 px**, y `.task__action` (Abrir/Eliminar) ronda los **24 px** de alto.

**AUD-33 (Media) — Colores de badges *hardcodeados*, fuera del sistema de tokens.**
Los badges definen colores literales que no están en `:root` ni tienen equivalente oscuro consistente: `.badge--today/soon` (`#fff4e5`/`#b45309`), `.badge--complete` (`#e7f8ef`/`#067647`) y `.badge--files` (`#f0edff`/`#6435c9`) (`app.css` 876-895), con overrides manuales repetidos en el bloque oscuro (897-913). Rompe la consistencia del tema.

**AUD-34 (Baja) — Radios inconsistentes (8px vs. token de 10px).**
Convive el token `--radius-sm: 10px` con 8 `border-radius: 8px` *hardcodeados* (líneas 206, 476, 535, 840, 988, 1106, 1166, 1500), lo que produce esquinas levemente distintas entre controles que deberían verse iguales.

**AUD-35 (Baja) — Sin confirmación para borrados secundarios.**
Solo el borrado de tarea pasa por `ConfirmDialog`. Borrar una subtarea, un enlace o un adjunto es inmediato e irreversible, lo que es inconsistente con el cuidado aplicado al borrado principal.

**AUD-36 (Baja) — Sin feedback explícito de éxito en crear/editar.**
Tras crear o editar, la única señal es el *refetch* implícito (la tarjeta aparece/actualiza). No hay toast ni confirmación; el único aviso existente es el de "Deshacer" tras eliminar.

**AUD-37 (Baja) — Toast invertido y truncado.**
En modo oscuro el toast se vuelve de fondo claro (invierte respecto del tema) y su mensaje usa `white-space: nowrap` con `text-overflow: ellipsis`, por lo que los avisos largos (p. ej. el de adjuntos fallidos) se recortan.

**AUD-38 (Baja) — Tipografías muy pequeñas.**
Varios textos quedan en 0.68–0.7rem (≈10–11 px): `.filter > span`, `.tag-chip`, `.app__header::before`, `.task__id`. Combinado con AUD-06 (contraste bajo de `--muted`) agrava la legibilidad.

## 7. Tabla consolidada de hallazgos

| ID | Dimensión | Componente / archivo (línea) | Descripción | Evidencia | Severidad | Impacto | Recomendación |
|---|---|---|---|---|---|---|---|
| AUD-01 | Accesibilidad | `components/TaskDetailModal.jsx`, `components/ConfirmDialog.jsx` | Sin trampa de foco, sin foco inicial ni restauración al cerrar | `TaskDetailModal` no usa refs de foco; `ConfirmDialog` enfoca `confirmRef` pero no atrapa el foco | Alta | Teclado/lector se pierde detrás del modal | Atrapar foco, enfocar el primer control al abrir y restaurar el foco al disparador |
| AUD-02 | Accesibilidad | `components/Column.jsx` (54-64), `components/TaskCard.jsx` (22) | Mover tareas solo por drag&drop, sin alternativa de teclado | `draggable="true"` + `handleDrop`; el modal no ofrece cambio de estado | Alta | Usuarios sin mouse no pueden cambiar de estado | Agregar control de estado (select/botones) en la tarjeta o en el modal |
| AUD-03 | Accesibilidad | `components/TaskDetailModal.jsx` (550-557), `styles/app.css` (1217-1219) | Input de archivo inalcanzable por teclado | `.upload input[type="file"] { display: none; }` | Alta | No se puede adjuntar en el modal con teclado | Usar `sr-only`/`clip` en vez de `display:none` y un `<label>` con `tabindex`/`for` |
| AUD-04 | Accesibilidad | `styles/app.css` (58-59, 160-161) | Botones con contraste bajo en modo oscuro | blanco sobre `#8b83ff` = 3.09:1; sobre `#a49cff` = 2.39:1 | Alta | Botones primarios ilegibles en oscuro | Oscurecer el fondo de `.btn` o usar texto oscuro en modo oscuro |
| AUD-05 | Accesibilidad | `styles/app.css` (24, 62-63, 615-623) | `.alert` ilegible en modo oscuro | `--danger-dark` `#c2262b` no se redefine; ratio 2.71:1 | Alta | Los errores globales no se leen en oscuro | Redefinir `--danger-dark` para el tema oscuro |
| AUD-06 | Accesibilidad | `styles/app.css` (17, 793-802, 637-642, 270-276) | `--muted` por debajo de 4.5:1 en claro | 3.87:1 (surface), 3.42:1 (bg), 3.64:1 (surface-2), 3.37:1 (surface-3) | Media | Texto de apoyo difícil de leer | Oscurecer `--muted` (p. ej. a `#5c6379`) en modo claro |
| AUD-07 | Accesibilidad | `styles/app.css` (100-103, 39) | Indicador de foco con contraste 1.19:1 | `outline:none` + `box-shadow: var(--ring)` con `--primary-soft` al 12% | Media | Foco apenas visible para baja visión | Añadir un anillo de foco de mayor contraste (≥3:1) |
| AUD-08 | Accesibilidad | `styles/app.css` (13, 283, 51) | Bordes de controles < 3:1 | `#cfd5e8` sobre `#f6f8fd` = 1.38:1; oscuro 1.66:1 | Media | Límites de input poco perceptibles | Usar un borde más oscuro (≥3:1 sobre el fondo del input) |
| AUD-09 | Accesibilidad | `components/TaskCard.jsx` (18-26) | Tarjeta clickeable no operable por teclado | `<article onClick=...>` sin `role`/`tabIndex`/`onKeyDown` | Media | Affordance no accesible (mitigado por botón "Abrir") | Hacer la tarjeta un `<button>`/`div role="button"` con `tabIndex` y manejo de Enter/Espacio |
| AUD-10 | Accesibilidad | `components/TaskDetailModal.jsx` (66-74) | Escape cierra el modal y descarta la edición | `handleKey` global llama `onClose()` sin chequear `editing` | Media | Pérdida de cambios sin aviso | Ignorar Escape o pedir confirmación cuando `editing` es true |
| AUD-11 | Accesibilidad | `styles/app.css` (1406-1414) | Badges de prioridad < 4.5:1 en claro | Alta 4.25:1, Media 4.28:1 | Media | Etiquetas de prioridad de bajo contraste | Ajustar el porcentaje de `color-mix` del texto |
| AUD-12 | Accesibilidad | `App.jsx` (261-262) | Carga sin anuncio para lector de pantalla | `<p className="loading">` sin `role`/`aria-live` | Media | Lector no anuncia inicio/fin de carga | `role="status"` o `aria-live="polite"` |
| AUD-13 | Accesibilidad | `components/TaskDetailModal.jsx` (254), `components/ConfirmDialog.jsx` (29) | Overlay `role="presentation"` con `onClick` | `onClick={onClose}` en div no enfocable | Baja | Cierre por fondo solo con mouse | Equivalente de teclado o quitar el rol |
| AUD-14 | Accesibilidad | `styles/app.css` (1291-1327) | Toast oscuro con contraste bajo | acción 2.74:1; cierre 2.56:1 | Baja | Acciones del aviso poco legibles | Ajustar colores en modo oscuro |
| AUD-15 | Rendimiento | `App.jsx` (199), `components/Board.jsx` (19) | Re-render total por cada tecla de búsqueda | `setQuery` por tecla; sin `memo`/`useMemo`; `filter` inline | Media | Trabajo de render evitable | `React.memo` en tarjetas/columnas y memoizar el filtrado |
| AUD-16 | Rendimiento | `App.jsx` (71), `components/TaskForm.jsx` (79-91) | Doble petición a `/tags` | `getTags()` en `App.load` y en `TaskForm` | Media | Petición redundante en el arranque | Reutilizar las etiquetas ya cargadas por `App` |
| AUD-17 | Rendimiento | `frontend/src` (sin `React.lazy`) | Sin code splitting / lazy loading | 0 importaciones dinámicas; bundle único de 253.73 kB | Media | Modal/aviso cargados siempre | `React.lazy` + `Suspense` para el modal |
| AUD-18 | Rendimiento | `vite.config.js` (sin `build`) | Chunk único sin separar vendor | No hay `manualChunks` | Baja | Cacheo menos eficiente | Definir `manualChunks` para React/ReactDOM |
| AUD-19 | Calidad | `App.jsx` (66-86) | Condición de carrera al cargar por filtros | `load` sin `AbortController`/id de request | Media | Datos obsoletos sobrescriben la lista | Cancelar peticiones previas o validar el orden con un id |
| AUD-20 | Calidad | `components/TaskForm.jsx` (21-23, 173-206), `components/TaskDetailModal.jsx` (13-15, 162-202) | Validación y constantes de enlaces duplicadas | Bloques casi idénticos en ambos archivos | Media | Reglas que pueden desincronizarse | Extraer validación y constantes a un módulo compartido |
| AUD-21 | Calidad | `components/TaskDetailModal.jsx` (41-617) | Componente sobredimensionado | ~560 líneas, 10 `useState`, 6 responsabilidades | Media | Difícil de mantener y testear | Dividir en subcomponentes por panel |
| AUD-22 | Calidad | `App.jsx` (71-74) | `Promise.all` acopla `/tags` al tablero | Fallo de `/tags` descarta `getTasks` válido | Media | El tablero no carga si fallan las etiquetas | Cargar etiquetas de forma independiente y tolerante a fallos |
| AUD-23 | Calidad | `api.js` (38-39) | Rama legacy `boolean` sin uso | `typeof options === "boolean"` | Baja | Código muerto | Eliminar la rama |
| AUD-24 | Calidad | `components/TaskForm.jsx` (387, 455, 532) | `key` basada en índice | `key={`${title}-${index}`}` etc. | Baja | Riesgo de reutilización incorrecta de DOM | Usar identificadores estables |
| AUD-25 | Calidad | `frontend/src` (sin Error Boundary) | Sin barrera de errores | No existe `ErrorBoundary` | Baja | Un throw deja la app en blanco | Envolver `App` en un Error Boundary con fallback |
| AUD-26 | Calidad | `components/TaskCard.jsx` (35), `components/TaskDetailModal.jsx` (251) | Slug de prioridad duplicado | `task.priority.toLowerCase()` en dos lugares | Baja | Micro-duplicación | Extraer un helper `prioritySlug()` |
| AUD-27 | Calidad | `App.jsx` (130-141) | Handlers recreados en cada render | Funciones no memoizadas pasadas a hijos | Baja | Impide memoización efectiva | `useCallback` donde corresponda |
| AUD-28 | Calidad | `api.js` (9), `App.jsx` (76) | Error de red mostrado en crudo | `fetch` sin try/catch; `setError(err.message)` | Baja | Mensaje técnico para el usuario | Traducir errores de red a mensajes en español |
| AUD-29 | UX | `components/TaskCard.jsx` (22), `components/Column.jsx` (54-64) | Drag&drop no funciona en táctil | API HTML5 DnD sin soporte táctil | Media | En móvil no se pueden mover tareas | Fallback táctil o control de estado alternativo |
| AUD-30 | UX | `App.jsx` (261-270), `styles/app.css` (625-629) | Carga reemplaza el tablero (salto de layout) | Render condicional loading vs. Board; sin skeleton | Media | Parpadeo y desorientación | Skeleton/spinner superpuesto sin desmontar el tablero |
| AUD-31 | UX | `components/TaskDetailModal.jsx` (420, 496, 550) | Acciones secundarias sin estado "enviando" | Solo submit/edición tienen `disabled` | Media | Dobles envíos por clics repetidos | Deshabilitar durante la operación |
| AUD-32 | UX | `styles/app.css` (201-215, 502-514, 832-844, 1308-1322) | Áreas táctiles < 44 px | `.icon-button` 27px, `.chip__remove` 18px, `.task__action` ~24px | Media | Difícil de tocar con el dedo | Ampliar padding/tamaño de los controles |
| AUD-33 | UX | `styles/app.css` (876-895, 897-913) | Badges con colores hardcodeados | `#fff4e5`, `#e7f8ef`, `#f0edff`, etc. fuera de tokens | Media | Inconsistencia del tema | Definir tokens de color para badges (claro y oscuro) |
| AUD-34 | UX | `styles/app.css` (206, 476, 535, 840, 988, 1106, 1166, 1500) | Radios inconsistentes (8px vs 10px) | 8 usos de `border-radius: 8px` junto a `--radius-sm: 10px` | Baja | Detalle visual dispar | Unificar con los tokens `--radius*` |
| AUD-35 | UX | `components/TaskDetailModal.jsx` (395-402, 460-467, 537-544) | Borrados secundarios sin confirmación | Solo el borrado de tarea usa `ConfirmDialog` | Baja | Borrado accidental de subtareas/adjuntos | Confirmación o "deshacer" para borrados secundarios |
| AUD-36 | UX | `App.jsx` (130-141) | Sin feedback de éxito al crear/editar | Solo `refetch`; el único aviso es el de deshacer | Baja | Usuario no sabe si la acción funcionó | Toast de confirmación breve |
| AUD-37 | UX | `styles/app.css` (1259-1289) | Toast invertido y truncado en oscuro | fondo `var(--text)` claro; `white-space: nowrap` | Baja | Aviso inconsistente y recortado | Ajustar estilo oscuro y permitir salto de línea |
| AUD-38 | UX | `styles/app.css` (1361, 1466, 127) | Tipografías muy pequeñas (~10-11 px) | `.filter > span` y `.tag-chip` en 0.68rem | Baja | Legibilidad reducida | Subir el tamaño mínimo de texto |

## 8. Resumen de métricas

**Total de hallazgos: 38**

| Severidad | Cantidad | Porcentaje |
|---|---|---|
| Alta | 5 | 13.2 % |
| Media | 19 | 50.0 % |
| Baja | 14 | 36.8 % |

| Dimensión | Cantidad | Alta | Media | Baja |
|---|---|---|---|---|
| Accesibilidad (a11y) | 14 | 5 | 7 | 2 |
| Rendimiento y bundle | 4 | 0 | 3 | 1 |
| Calidad de código React | 10 | 0 | 4 | 6 |
| UX y consistencia visual | 10 | 0 | 5 | 5 |
| **Total** | **38** | **5** | **19** | **14** |

**Estado tras la fase de remediación:** los **38 hallazgos** fueron corregidos en el código del cliente (no aplica ninguno). El detalle por hallazgo está en la sección 12.

| Estado | Cantidad | Porcentaje |
|---|---|---|
| Corregido | 38 | 100 % |
| No aplica | 0 | 0 % |
| Pendiente | 0 | 0 % |

**Indicadores positivos verificados:** `npm run build` sin advertencias (JS 253.73 kB / 77.25 kB gzip); `npm run lint` en 0 problemas; HTML semántico correcto en el tablero; etiquetas de formulario correctamente asociadas; modales con ARIA básica y cierre con Escape; estados vacíos en columnas y paneles; modo oscuro y `prefers-reduced-motion` contemplados; ninguna imagen sin texto alternativo (no hay imágenes).

## 9. Top 5 de prioridades

1. **AUD-01 (Alta) — Gestión y trampa de foco en los modales.** Es el problema de accesibilidad más estructural: afecta a ambos modales y a toda la navegación por teclado/lector de pantalla.
2. **AUD-04 (Alta) — Contraste de botones en modo oscuro (2.39:1–3.09:1).** Hace ilegibles *todos* los botones primarios para quienes usan el tema oscuro; corrección acotada y de alto impacto.
3. **AUD-06 (Alta/Media) — Contraste de `--muted` en modo claro (3.37:1–3.87:1).** Se propaga a descripciones, etiquetas, ayudas y contadores: es el ajuste de contraste que más superficie cubre.
4. **AUD-02 (Alta) — Sin alternativa de teclado para mover tareas** (emparentado con AUD-29 en móvil). Bloquea la funcionalidad central del producto a usuarios de teclado y a dispositivos táctiles.
5. **AUD-19 (Media) — Condición de carrera en la carga por filtros.** Es el riesgo funcional más concreto de la capa de estado: puede mostrar datos obsoletos de forma intermitente y difícil de reproducir.

## 10. Conclusión

El frontend del *Tablero de Tareas* está **mejor construido que el promedio de un trabajo académico**: compila sin advertencias, pasa el linter sin una sola observación, usa HTML semántico en el tablero, asocia correctamente las etiquetas de formulario, contempla estados vacíos, modo oscuro y reducción de movimiento, y no arrastra peso innecesario (sin imágenes ni fuentes descargadas).

Las debilidades se concentran en tres frentes:

- **Accesibilidad (5 hallazgos altos).** Es la dimensión con mayor deuda: falta gestión/trampa de foco en modales, no hay operación por teclado para mover tareas ni para adjuntar archivos en el modal, y —de forma transversal— varios pares de color incumplen WCAG 1.4.3/1.4.11, con especial gravedad en modo oscuro (botones 2.39:1 y avisos de error 2.71:1).
- **Rendimiento y estado.** El único bundle (253.73 kB) es aceptable, pero hay trabajo evitable: re-render completo del tablero al tipear, doble carga de etiquetas, ausencia de *code splitting* y una condición de carrera en la recarga por filtros.
- **Consistencia y mantenibilidad.** Duplicación de reglas (validación de enlaces), un componente modal sobredimensionado, colores/radios *hardcodeados* y feedback desigual (algunas acciones sin estado de carga ni confirmación).

Ninguno de los hallazgos es de gravedad crítica para una demo, pero los cinco altos —encabezados por el foco en modales y el contraste en modo oscuro— deberían abordarse antes de considerar el cliente "accesible". El resto constituye una lista de mejoras priorizada y de bajo riesgo para futuras iteraciones.

**Resultado de la remediación.** Tras esta auditoría se ejecutó una fase de corrección sobre `frontend/src/**` que resolvió **los 38 hallazgos** (sección 12). Los cambios se verificaron de forma real: `npm run lint` termina con **0 problemas**, `npm run build` compila **sin errores** y con *code splitting* efectivo (`TaskDetailModal` en su propio chunk y un chunk de *vendor* para React), el recálculo de contraste WCAG deja **todos los pares por encima de su umbral** en ambos temas, y la suite de sistema completa (80 casos: 62 API + 11 UI + 7 caja blanca) se ejecutó sobre el backend con base temporal y pasó **80/80**. Ningún hallazgo quedó como "no aplica": todos admitían una corrección concreta y de bajo riesgo que se implementó.

## 11. Evidencias adjuntas

Guardadas en `docs/evidencias/auditoria_frontend/`:

- `npm_run_build.txt` — salida cruda de `npm run build` (fase de auditoría).
- `npm_run_build.txt` (regenerado en la remediación) — build final con *code splitting*.
- `npm_run_lint.txt` — salida cruda de `npm run lint` (final, 0 problemas).
- `contraste_wcag.txt` — cálculo de ratios de contraste WCAG de la auditoría (claro y oscuro).
- `contraste_corregido.txt` — recálculo de ratios tras la corrección; todos los pares cumplen.
- `calcular_contraste_corregido.py` — script que reproduce el recálculo.

## 12. Estado de remediación de hallazgos

Todas las correcciones se aplicaron sobre el código del cliente (`frontend/src/**`), respetando las restricciones del proyecto: no se alteraron los atributos `data-testid` ni los selectores usados por la suite de Etapa 6, no se modificó el texto de error del título ("El título es obligatorio y no puede contener solo espacios.") y no se tocó el backend ni la API.

| ID | Severidad | Estado | Corrección aplicada | Evidencia |
|---|---|---|---|---|
| AUD-01 | Alta | Corregido | Hook `useFocusTrap` en `TaskDetailModal` y `ConfirmDialog`: enfoca el primer control, atrapa Tab/Shift+Tab y restaura el foco al disparador al cerrar. | `frontend/src/useFocusTrap.js`; `npm_run_lint.txt`; suite 80/80 |
| AUD-02 | Alta | Corregido | Control `<select data-testid="detail-status">` en el panel Detalle para cambiar de estado (alternativa de teclado/ratón al *drag & drop*). | `components/TaskDetailModal.jsx`; `app.css` (AUD-02/AUD-29); CP-UI-03 |
| AUD-03 | Alta | Corregido | `.upload input[type="file"]` pasa de `display:none` a *sr-only* (1px, `clip`) con `.upload:focus-within`; el control es enfocable. | `styles/app.css` (AUD-03) |
| AUD-04 | Alta | Corregido | Fondos de botón oscurecidos en ambos temas (claro `#5b53e8`/`#443ccd`; oscuro `#4f46e5`/`#3730a3`): blanco ≥ 4.90:1. | `app.css` (AUD-04); `contraste_corregido.txt` |
| AUD-05 | Alta | Corregido | `--danger-dark` redefinido en modo oscuro (`#ffb4b6`): `.alert` queda en 8.39:1. | `app.css` (AUD-05); `contraste_corregido.txt` |
| AUD-06 | Media | Corregido | `--muted` claro pasa a `#5c6379`; ratios 5.20–5.97:1 sobre todas las superficies. | `app.css` (AUD-06); `contraste_corregido.txt` |
| AUD-07 | Media | Corregido | Anillo de foco con color sólido `#443ccd` (claro) / `#8b83ff` (oscuro); 5.56–7.57:1. | `app.css` (AUD-07); `contraste_corregido.txt` |
| AUD-08 | Media | Corregido | `--border-strong` a `#7c829b` (claro) y `#7c85b4` (oscuro); bordes ≥ 3.31:1. | `app.css` (AUD-08); `contraste_corregido.txt` |
| AUD-09 | Media | Corregido | `TaskCard` como `<article role="button" tabIndex={0} aria-label onKeyDown>` con activación por Enter/Espacio. | `components/TaskCard.jsx` |
| AUD-10 | Media | Corregido | Escape gestionado por `useFocusTrap` con `onEscape` que cierra **solo** si no hay edición en curso. | `components/TaskDetailModal.jsx`; `useFocusTrap.js` |
| AUD-11 | Media | Corregido | Color de texto de los badges de prioridad ajustado: Alta 4.73:1, Media 5.57:1. | `app.css` (AUD-11); `contraste_corregido.txt` |
| AUD-12 | Media | Corregido | Estado de carga con `role="status"` y `aria-live="polite"`. | `App.jsx` |
| AUD-13 | Baja | Corregido | Se eliminó `role="presentation"` de los overlays; el cierre por Escape (teclado) queda cubierto por la trampa de foco. | `TaskDetailModal.jsx`, `ConfirmDialog.jsx` |
| AUD-14 | Baja | Corregido | Toast en modo oscuro sobre superficie oscura (`--toast-*`): acción 7.19:1, cierre 10.46:1. | `app.css` (AUD-14/AUD-37); `contraste_corregido.txt` |
| AUD-15 | Media | Corregido | `React.memo` en `Board`/`Column`/`TaskCard`, `useMemo` del agrupado por estado y `useCallback` en los handlers de `App`. | `components/Board.jsx`, `Column.jsx`, `TaskCard.jsx`; `App.jsx` |
| AUD-16 | Media | Corregido | `TaskForm` recibe `tagOptions` por props; ya no vuelve a pedir `/tags`. | `components/TaskForm.jsx`, `App.jsx` |
| AUD-17 | Media | Corregido | `React.lazy` + `Suspense` para `TaskDetailModal`; chunk propio de 11.52 kB (gzip 3.32 kB). | `App.jsx`; `npm_run_build.txt` |
| AUD-18 | Baja | Corregido | `build.rollupOptions.output.manualChunks` separa React/ReactDOM en un chunk de *vendor* (218.72 kB). | `vite.config.js`; `npm_run_build.txt` |
| AUD-19 | Media | Corregido | `load` usa un identificador de petición (`requestRef`) y descarta respuestas obsoletas. | `App.jsx` |
| AUD-20 | Media | Corregido | Constantes y `validateLink()` extraídos al módulo compartido `links.js`, usado por formulario y detalle. | `frontend/src/links.js`; `DetailLinks.jsx`, `TaskForm.jsx` |
| AUD-21 | Media | Corregido | `TaskDetailModal` dividido en `DetailChecklist`, `DetailLinks`, `DetailAttachments` y `DetailHistory`; el orquestador bajó a ~246 líneas. | `components/Detail*.jsx`, `TaskDetailModal.jsx` |
| AUD-22 | Media | Corregido | `getTags().catch(() => null)` desacopla el fallo de `/tags` de la carga del tablero. | `App.jsx` |
| AUD-23 | Baja | Corregido | Eliminada la rama muerta `typeof options === "boolean"`; `getTasks(options = {})`. | `api.js` |
| AUD-24 | Baja | Corregido | Borradores de subtareas/enlaces/archivos con `id` estable (`uidRef`) y `key={item.id}`. | `components/TaskForm.jsx` |
| AUD-25 | Baja | Corregido | `ErrorBoundary` con `getDerivedStateFromError`/`componentDidCatch` y fallback `role="alert"` envolviendo la app. | `components/ErrorBoundary.jsx`; `main.jsx` |
| AUD-26 | Baja | Corregido | Helper `prioritySlug()` en `format.js`, reutilizado por tarjeta y detalle. | `frontend/src/format.js` |
| AUD-27 | Baja | Corregido | Handlers de `App` memoizados con `useCallback`. | `App.jsx` |
| AUD-28 | Baja | Corregido | `api.js` envuelve `fetch` y traduce el fallo de red a un mensaje en español ("No se pudo conectar con el servidor..."). | `api.js` |
| AUD-29 | Media | Corregido | El control de estado (AUD-02) da alternativa al *drag & drop* no táctil en móviles/tabletas. | `TaskDetailModal.jsx`; `app.css` (AUD-02/AUD-29) |
| AUD-30 | Media | Corregido | `.board-overlay` con chip superpuesto (`role="status"`) durante la recarga; el tablero ya no se desmonta. | `App.jsx`; `app.css` (AUD-30) |
| AUD-31 | Media | Corregido | Paneles de checklist/enlaces/adjuntos con estado `busy` que deshabilita los botones durante la operación. | `DetailChecklist.jsx`, `DetailLinks.jsx`, `DetailAttachments.jsx` |
| AUD-32 | Media | Corregido | Áreas táctiles ≥ 44 px en `.icon-button`, `.task__action`, `.toast__close` y `.chip__remove::after`. | `app.css` (AUD-32) |
| AUD-33 | Media | Corregido | Colores de badges movidos a tokens del tema (`--badge-*-bg`/`--badge-*-fg`) definidos para claro y oscuro. | `app.css` (AUD-33); `contraste_corregido.txt` |
| AUD-34 | Baja | Corregido | Los `border-radius: 8px` *hardcodeados* se reemplazaron por el token `--radius-sm`. | `app.css` |
| AUD-35 | Baja | Corregido | Borrados secundarios (subtarea, enlace, adjunto) ofrecen un toast "Deshacer" que re-crea el elemento. | `DetailChecklist.jsx`, `DetailLinks.jsx`, `DetailAttachments.jsx` |
| AUD-36 | Baja | Corregido | Toasts de éxito al crear ("Tarea creada correctamente.") y al editar ("Cambios guardados."). | `App.jsx` |
| AUD-37 | Baja | Corregido | Toast oscuro sobre superficie oscura (sin invertir) y `.toast__message` permite salto de línea. | `app.css` (AUD-37) |
| AUD-38 | Baja | Corregido | Tamaños mínimos de texto subidos (≥ 0.75 rem ≈ 12 px) en filtros, chips y textos pequeños. | `app.css` (AUD-38) |

**Resumen:** 38/38 corregidos (Alta 5/5, Media 19/19, Baja 14/14); 0 no aplica; 0 pendientes.

**Verificación de la remediación (evidencia real):**

- `npm run lint` → 0 problemas (código de salida 0). Evidencia: `npm_run_lint.txt`.
- `npm run build` → exitoso con *code splitting*: `TaskDetailModal-*.js` 11.52 kB (gzip 3.32), `index-*.js` 29.70 kB (gzip 9.30) y `react-*.js` 218.72 kB (gzip 68.24); 35 módulos. Evidencia: `npm_run_build.txt`.
- Contraste WCAG recalculado → **todos** los pares cumplen su umbral (4.5:1 texto, 3:1 texto grande/componentes) en claro y oscuro. Evidencia: `contraste_corregido.txt`.
- Suite de sistema (80 casos) sobre backend con base temporal (`KANBAN_DB_PATH=/tmp/kanban_etapa6.db`): **80/80 aprobados** (API 62/62, UI 11/11, caja blanca 7/7); backend restaurado después y `GET /api/health` → 200.
