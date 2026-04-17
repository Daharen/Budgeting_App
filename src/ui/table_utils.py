from __future__ import annotations

from PySide6.QtWidgets import QTableWidgetItem


def item(v: object) -> QTableWidgetItem:
    return QTableWidgetItem('' if v is None else str(v))
