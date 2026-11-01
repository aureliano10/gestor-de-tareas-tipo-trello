"""Prueba unitaria del helper ``is_overdue`` (Etapa 12, ciclo TDD).

Se escribió **antes** que la implementación. En la primera corrida el
import falla porque el helper todavía no existe (RED) y, una vez agregado
al repositorio, el caso pasa (GREEN).
"""

from __future__ import annotations

from app.repository import is_overdue


def test_cp_un_19_is_overdue_regla_de_vencimiento():
    """Una tarea vence cuando su fecha es anterior a hoy y no está terminada."""
    today = "2026-11-01"

    # Vencida: fecha anterior a hoy y tarea no finalizada.
    assert is_overdue("2026-10-31", "Pendiente", today) is True
    assert is_overdue("2026-10-31", "En curso", today) is True

    # No vencida: la fecha de hoy o una futura no vencen.
    assert is_overdue("2026-11-01", "Pendiente", today) is False
    assert is_overdue("2026-11-02", "Pendiente", today) is False

    # No vencida: una tarea terminada nunca se marca como vencida.
    assert is_overdue("2026-10-31", "Terminada", today) is False

    # No vencida: sin fecha límite.
    assert is_overdue(None, "Pendiente", today) is False
