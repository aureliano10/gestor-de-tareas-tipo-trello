# DEF-01 - Migracion de esquema: antes y despues

Archivo: `backend/app/database.py`
Funcion afectada: `_migrate_tasks`

## Antes (version con el defecto)

Commit de referencia: `7d506a4` - "reconstruccion de proyecto hasta la etapa 6".
Fragmento obtenido con `git show 7d506a4:backend/app/database.py`.

```python
def _migrate_tasks(conn: sqlite3.Connection) -> None:
    conn.execute("ALTER TABLE tasks RENAME TO tasks_legacy")
    conn.execute(CREATE_TASKS_TABLE)
    conn.execute(
        """
        INSERT INTO tasks (id, title, description, status, due_date, position,
                           deleted_at, created_at)
        SELECT id, title, '', status, NULL, 0, NULL, created_at
        FROM tasks_legacy
        """
    )
    conn.execute("DROP TABLE tasks_legacy")
    conn.execute(
        """
        UPDATE tasks SET position = (
            SELECT COUNT(*) FROM tasks AS previous
            WHERE previous.status = tasks.status
              AND previous.id < tasks.id
        )
        """
    )
```

El problema: al ejecutar `ALTER TABLE tasks RENAME TO tasks_legacy`, SQLite
reescribe las claves foraneas de las tablas dependientes (`subtasks` y
`attachments`) para que apunten a `tasks_legacy`. Cuando la migracion termina
con `DROP TABLE tasks_legacy`, esas claves foraneas quedan apuntando a una tabla
inexistente y todo `INSERT` sobre `subtasks` o `attachments` falla con
`no such table: main.tasks_legacy`.

## Despues (version corregida)

Commit `56010e9` - "Etapa 7 (backend): prioridad, responsable, etiquetas, enlaces,
historial y filtros". Este es el estado vigente del archivo.

```python
def _table_columns(conn: sqlite3.Connection, name: str) -> set[str]:
    return {
        row["name"] for row in conn.execute(f"PRAGMA table_info({name})").fetchall()
    }


REQUIRED_TASK_COLUMNS = {
    "description",
    "due_date",
    "position",
    "deleted_at",
    "priority",
    "assignee",
}

# Definiciones usadas para completar columnas faltantes de forma aditiva.
MISSING_TASK_COLUMN_DEFINITIONS = {
    "description": "description TEXT NOT NULL DEFAULT ''",
    "due_date": "due_date TEXT",
    "position": "position INTEGER NOT NULL DEFAULT 0",
    "deleted_at": "deleted_at TEXT",
    "priority": "priority TEXT NOT NULL DEFAULT 'Media'",
    "assignee": "assignee TEXT NOT NULL DEFAULT ''",
}


def _needs_migration(conn: sqlite3.Connection) -> bool:
    """Detecta si a `tasks` le falta alguna columna esperada del esquema."""
    if _table_sql(conn, "tasks") is None:
        return False
    return bool(REQUIRED_TASK_COLUMNS - _table_columns(conn, "tasks"))


def _migrate_tasks(conn: sqlite3.Connection) -> None:
    """Migracion aditiva: agrega las columnas faltantes sin recrear la tabla.

    No se renombra ni se recrea `tasks` para no romper las claves foraneas de
    subtasks/attachments que apuntan a esta tabla.
    """
    columns = _table_columns(conn, "tasks")
    for name, definition in MISSING_TASK_COLUMN_DEFINITIONS.items():
        if name not in columns:
            conn.execute(f"ALTER TABLE tasks ADD COLUMN {definition}")
```

## Diferencia principal

| Aspecto | Version con el defecto | Version corregida |
|---------|------------------------|-------------------|
| Estrategia | Recrear la tabla (RENAME + CREATE + INSERT + DROP) | Aditiva (ALTER TABLE ... ADD COLUMN) |
| Deteccion | Presencia de CHECK o de columnas nuevas | Columnas faltantes segun REQUIRED_TASK_COLUMNS |
| Efecto sobre claves foraneas | Las reescribe a `tasks_legacy` y las deja rotas | No las toca |
| Resultado | INSERT en subtasks/attachments fallaba con 500 | INSERT funcionaba con 201 |

La correccion preserva la identidad de la tabla `tasks`, por lo que las claves
foraneas de `subtasks` y `attachments` siguen apuntando al nombre correcto y las
altas de subtareas y adjuntos vuelven a responder HTTP 201.
