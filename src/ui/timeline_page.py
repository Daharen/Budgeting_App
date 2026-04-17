from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class TimelinePage(QWidget):
    def __init__(self, refresh_cb):
        super().__init__()
        self.refresh_cb = refresh_cb
        self.show_history = QCheckBox('Show history')
        self.show_history.stateChanged.connect(self.refresh_cb)
        self.refresh_btn = QPushButton('Refresh Timeline')
        self.refresh_btn.clicked.connect(self.refresh_cb)

        controls = QHBoxLayout()
        controls.addWidget(self.show_history)
        controls.addWidget(self.refresh_btn)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(
            ['Date', 'Kind', 'Category', 'Description', 'Amount', 'Running Balance', 'Status', 'Required']
        )
        self.table.horizontalHeader().setStretchLastSection(True)

        layout = QVBoxLayout()
        layout.addLayout(controls)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def render(self, rows: list[dict]) -> None:
        today = date.today().isoformat()
        filtered = rows if self.show_history.isChecked() else [r for r in rows if r['date'] >= today]
        self.table.setRowCount(len(filtered))
        for i, row in enumerate(filtered):
            values = [
                row['date'], row['kind'], row['category'], row['description'],
                f"{row['amount']:.2f}", f"{row['running_balance']:.2f}", row['status'], str(row['required']),
            ]
            for c, value in enumerate(values):
                cell = QTableWidgetItem(value)
                if row.get('is_negative'):
                    cell.setBackground(QColor(255, 220, 220))
                if row['kind'] == 'projected':
                    cell.setForeground(QColor(90, 90, 90))
                cell.setFlags(cell.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(i, c, cell)
