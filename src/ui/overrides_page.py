from __future__ import annotations

from datetime import datetime, timezone
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QTableWidget, QVBoxLayout, QWidget

from src.ui.table_utils import item


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class OverridesPage(QWidget):
    def __init__(self, conn, refresh_cb):
        super().__init__()
        self.conn = conn
        self.refresh_cb = refresh_cb
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            'Source Kind', 'Source ID', 'Effective Date', 'Override Kind', 'Replacement Date', 'Replacement Amount', 'Skip', 'Notes'
        ])

        add_btn = QPushButton('Add Row')
        add_btn.clicked.connect(self.add_row)
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save)

        btns = QHBoxLayout()
        btns.addWidget(add_btn)
        btns.addWidget(save_btn)
        layout = QVBoxLayout()
        layout.addLayout(btns)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load(self):
        rows = self.conn.execute(
            '''SELECT source_kind, source_id, effective_date, override_kind, replacement_date, replacement_amount, is_skip, notes
               FROM timeline_overrides ORDER BY id'''
        ).fetchall()
        self.table.setRowCount(len(rows))
        keys = ['source_kind', 'source_id', 'effective_date', 'override_kind', 'replacement_date', 'replacement_amount', 'is_skip', 'notes']
        for r, row in enumerate(rows):
            for c, k in enumerate(keys):
                self.table.setItem(r, c, item(row[k]))

    def add_row(self):
        self.table.insertRow(self.table.rowCount())

    def save(self):
        with self.conn:
            self.conn.execute('DELETE FROM timeline_overrides')
            for r in range(self.table.rowCount()):
                vals = [self.table.item(r, c).text() if self.table.item(r, c) else '' for c in range(8)]
                if not vals[0] or not vals[1] or not vals[2]:
                    continue
                self.conn.execute(
                    '''INSERT INTO timeline_overrides(source_kind, source_id, effective_date, override_kind, replacement_date, replacement_amount,
                            is_skip, notes, created_utc, updated_utc)
                       VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (vals[0], int(vals[1]), vals[2], vals[3] or 'manual', vals[4] or None,
                     float(vals[5]) if vals[5] else None, int(vals[6] or 0), vals[7], now_iso(), now_iso()),
                )
        self.refresh_cb()
