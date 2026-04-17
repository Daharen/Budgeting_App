from __future__ import annotations

from datetime import datetime, timezone
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QTableWidget, QVBoxLayout, QWidget

from src.ui.table_utils import item


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ActualsPage(QWidget):
    def __init__(self, conn, refresh_cb):
        super().__init__()
        self.conn = conn
        self.refresh_cb = refresh_cb
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(['Date', 'Account ID', 'Category ID', 'Description', 'Amount', 'Direction', 'Status'])

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
            'SELECT transaction_date, account_id, category_id, description, amount, direction, status FROM actual_transactions ORDER BY transaction_date'
        ).fetchall()
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, k in enumerate(['transaction_date', 'account_id', 'category_id', 'description', 'amount', 'direction', 'status']):
                self.table.setItem(r, c, item(row[k]))

    def add_row(self):
        r = self.table.rowCount()
        self.table.insertRow(r)

    def save(self):
        with self.conn:
            self.conn.execute('DELETE FROM actual_transactions')
            for r in range(self.table.rowCount()):
                vals = [self.table.item(r, c).text() if self.table.item(r, c) else '' for c in range(7)]
                if not vals[0] or not vals[3] or not vals[4]:
                    continue
                self.conn.execute(
                    '''INSERT INTO actual_transactions(account_id, category_id, transaction_date, description, amount, direction, status, notes, created_utc, updated_utc)
                       VALUES(?, ?, ?, ?, ?, ?, ?, '', ?, ?)''',
                    (int(vals[1] or 1), int(vals[2]) if vals[2] else None, vals[0], vals[3], float(vals[4]), vals[5] or 'outflow', vals[6] or 'posted', now_iso(), now_iso()),
                )
        self.refresh_cb()
