from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget


class SummaryPage(QWidget):
    def __init__(self, conn, refresh_cb):
        super().__init__()
        self.conn = conn
        self.refresh_cb = refresh_cb

        self.current_balance = QLineEdit('0.00')
        self.first_negative = QLineEdit()
        self.first_negative.setReadOnly(True)
        self.worst_dip = QLineEdit()
        self.worst_dip.setReadOnly(True)
        self.net_30 = QLineEdit(); self.net_30.setReadOnly(True)
        self.net_60 = QLineEdit(); self.net_60.setReadOnly(True)
        self.net_90 = QLineEdit(); self.net_90.setReadOnly(True)

        save_btn = QPushButton('Save Current Balance')
        save_btn.clicked.connect(self.save_current_balance)

        form = QFormLayout()
        form.addRow('Current balance', self.current_balance)
        form.addRow('', save_btn)
        form.addRow('First negative date', self.first_negative)
        form.addRow('Worst projected dip', self.worst_dip)
        form.addRow('30 day net', self.net_30)
        form.addRow('60 day net', self.net_60)
        form.addRow('90 day net', self.net_90)

        wrapper = QVBoxLayout()
        wrapper.addLayout(form)
        self.setLayout(wrapper)

    def load(self):
        row = self.conn.execute("SELECT value FROM app_settings WHERE key='current_balance'").fetchone()
        if row:
            self.current_balance.setText(row['value'])

    def render(self, summary):
        self.first_negative.setText(summary.first_negative_date or 'None')
        self.worst_dip.setText(
            f"{summary.lowest_projected_balance:.2f}" + (f" on {summary.lowest_projected_date}" if summary.lowest_projected_date else '')
        )
        self.net_30.setText(f'{summary.net_30:.2f}')
        self.net_60.setText(f'{summary.net_60:.2f}')
        self.net_90.setText(f'{summary.net_90:.2f}')

    def save_current_balance(self):
        with self.conn:
            self.conn.execute(
                "INSERT INTO app_settings(key, value) VALUES('current_balance', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (self.current_balance.text(),),
            )
        self.refresh_cb()
