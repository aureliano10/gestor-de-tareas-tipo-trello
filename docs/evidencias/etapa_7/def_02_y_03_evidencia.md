# DEF-02 y DEF-03 - Evidencia

## DEF-02 - Boton de alta de tarea sin estilo

Archivo: `frontend/src/components/TaskForm.jsx`

### Antes

Commit `f921ee8` (Etapa 3), obtenido con
`git show f921ee8:frontend/src/components/TaskForm.jsx`:

```jsx
<button type="submit" disabled={submitting}>
  {submitting ? "Agregando..." : "Agregar"}
</button>
```

Sin el atributo `className` el navegador aplicaba su estilo por defecto, por lo
que el boton quedaba visualmente inconsistente con el resto de la interfaz.

### Despues (estado actual)

```jsx
<button
  type="submit"
  className="btn"
  data-testid="task-submit"
  disabled={submitting}
>
  {submitting ? "Agregando..." : "Agregar tarea"}
</button>
```

La clase `btn` es el boton primario definido en el CSS del frontend. El cambio
se incorporo en el commit `7d506a4` y se mantiene en el estado vigente del
archivo.

## DEF-03 - Locator del caso CP-UI-09

El caso de interfaz CP-UI-09 ubicaba la tarjeta con un locator compuesto armado
a mano que no resolvia y provocaba un timeout; el problema estaba en el script
de pruebas, no en el sistema.

### Correccion

Se utilizo el helper `task_in` del arnes `scripts/etapa_6/ui_helpers.py`, que
compone el locator de forma consistente con el resto de los casos:

```python
def task_in(page, status: str, title: str):
    return page.locator(f'.column[data-status="{status}"] .task', has_text=title)
```

Uso en el caso corregido (`scripts/etapa_6/ejecutar_ui.py`):

```python
card_locator = task_in(page, "Pendiente", title)
card_locator.wait_for(timeout=10000)
```

### Resultado verificado

Tras la correccion el caso paso en la corrida del 01/11/2026. Registro de
`docs/evidencias/etapa_6/resultados_ui.json`:

    "id": "CP-UI-09",
    "passed": true,
    "resultado_obtenido": "insignia='Alta'; responsable='Ana'"

Y en `docs/evidencias/etapa_6/ejecucion.log`:

    CP-UI-09: APROBADO | insignia='Alta'; responsable='Ana'
