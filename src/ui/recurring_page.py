from __future__ import annotations

from datetime import datetime, timezone, date
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QTableWidget, QVBoxLayout, QWidget

from src.ui.table_utils import item


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RecurringPage(QWidget):
    def __init__(self, conn, refresh_cb):
        super().__init__()
        self.conn = conn
        self.refresh_cb = refresh_cb

        self.table = QTableWidget(0, 11)
        self.table.setHorizontalHeaderLabels([
            'Name', 'Account ID', 'Category ID', 'Amount', 'Direction', 'Cadence', 'Interval',
            'Day of Month', 'Day of Week', 'Start Date', 'Required'
        ])

        self.income_table = QTableWidget(0, 6)
        self.income_table.setHorizontalHeaderLabels(['Name', 'Start Date', 'Cadence', 'Interval', 'Amount', 'Active'])

        add_btn = QPushButton('Add Obligation')
        add_btn.clicked.connect(lambda: self.table.insertRow(self.table.rowCount()))
        add_income_btn = QPushButton('Add Income Rule')
        add_income_btn.clicked.connect(lambda: self.income_table.insertRow(self.income_table.rowCount()))
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save)

        btns = QHBoxLayout()
        btns.addWidget(add_btn)
        btns.addWidget(add_income_btn)
        btns.addWidget(save_btn)
        layout = QVBoxLayout()
        layout.addLayout(btns)
        layout.addWidget(QLabel('Recurring Obligations'))
        layout.addWidget(self.table)
        layout.addWidget(QLabel('Income Rules'))
        layout.addWidget(self.income_table)
        self.setLayout(layout)

    def load(self):
        rows = self.conn.execute(
            '''SELECT name, account_id, category_id, base_amount, direction, cadence_type, cadence_interval,
                      day_of_month, day_of_week, start_date, is_required
               FROM recurring_templates WHERE is_active = 1 ORDER BY id'''
        ).fetchall()
        self.table.setRowCount(len(rows))
        keys = ['name', 'account_id', 'category_id', 'base_amount', 'direction', 'cadence_type', 'cadence_interval', 'day_of_month', 'day_of_week', 'start_date', 'is_required']
        for r, row in enumerate(rows):
            for c, k in enumerate(keys):
                self.table.setItem(r, c, item(row[k]))

        incomes = self.conn.execute(
            'SELECT name, start_date, cadence_type, cadence_interval, base_amount, is_active FROM income_rules ORDER BY id'
        ).fetchall()
        self.income_table.setRowCount(len(incomes))
        for r, row in enumerate(incomes):
            for c, k in enumerate(['name', 'start_date', 'cadence_type', 'cadence_interval', 'base_amount', 'is_active']):
                self.income_table.setItem(r, c, item(row[k]))

    def save(self):
        with self.conn:
            self.conn.execute('DELETE FROM recurring_templates')
            for r in range(self.table.rowCount()):
                vals = [self.table.item(r, c).text() if self.table.item(r, c) else '' for c in range(11)]
                if not vals[0] or not vals[3]:
                    continue
                self.conn.execute(
                    '''INSERT INTO recurring_templates(account_id, category_id, name, base_amount, direction, cadence_type, cadence_interval,
                            day_of_month, day_of_week, start_date, end_date, is_required, is_active, notes, created_utc, updated_utc)
                       VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, 1, '', ?, ?)''',
                    (
                        int(vals[1] or 1), int(vals[2]) if vals[2] else None, vals[0], float(vals[3]), vals[4] or 'outflow',
                        vals[5] or 'monthly', int(vals[6] or 1), int(vals[7]) if vals[7] else None,
                        int(vals[8]) if vals[8] else None, vals[9] or date.today().isoformat(), int(vals[10] or 1), now_iso(), now_iso()
                    ),
                )

            self.conn.execute('DELETE FROM income_rules')
            for r in range(self.income_table.rowCount()):
                vals = [self.income_table.item(r, c).text() if self.income_table.item(r, c) else '' for c in range(6)]
                if not vals[0] or not vals[4]:
                    continue
                self.conn.execute(
                    '''INSERT INTO income_rules(name, start_date, end_date, cadence_type, cadence_interval, base_amount, notes, is_active, created_utc, updated_utc)
                       VALUES(?, ?, NULL, ?, ?, ?, '', ?, ?, ?)''',
                    (vals[0], vals[1] or date.today().isoformat(), vals[2] or 'weekly', int(vals[3] or 2), float(vals[4]), int(vals[5] or 1), now_iso(), now_iso()),
                )
        self.refresh_cb()
