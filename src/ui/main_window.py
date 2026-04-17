from __future__ import annotations

from datetime import date
from PySide6.QtWidgets import QMainWindow, QTabWidget

from src.core.timeline_service import TimelineService
from src.ui.actuals_page import ActualsPage
from src.ui.overrides_page import OverridesPage
from src.ui.recurring_page import RecurringPage
from src.ui.summary_page import SummaryPage
from src.ui.timeline_page import TimelinePage


class MainWindow(QMainWindow):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.timeline_service = TimelineService(conn)

        self.tabs = QTabWidget()

        self.timeline_page = TimelinePage(refresh_cb=self.refresh_all)
        self.recurring_page = RecurringPage(conn=conn, refresh_cb=self.refresh_all)
        self.actuals_page = ActualsPage(conn=conn, refresh_cb=self.refresh_all)
        self.overrides_page = OverridesPage(conn=conn, refresh_cb=self.refresh_all)
        self.summary_page = SummaryPage(conn=conn, refresh_cb=self.refresh_all)

        self.tabs.addTab(self.timeline_page, 'Timeline')
        self.tabs.addTab(self.recurring_page, 'Recurring')
        self.tabs.addTab(self.actuals_page, 'Actuals')
        self.tabs.addTab(self.overrides_page, 'Overrides')
        self.tabs.addTab(self.summary_page, 'Summary')

        self.setCentralWidget(self.tabs)
        self.setWindowTitle('Budgeting Timeline Planner')
        self.resize(1200, 700)

        self.refresh_all()

    def refresh_all(self):
        self.recurring_page.load()
        self.actuals_page.load()
        self.overrides_page.load()
        self.summary_page.load()

        rows, summary = self.timeline_service.generate(
            as_of=date.today(),
            days_forward=90,
            include_history=self.timeline_page.show_history.isChecked(),
        )
        self.timeline_page.render(rows)
        self.summary_page.render(summary)
