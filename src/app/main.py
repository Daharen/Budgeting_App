from __future__ import annotations

import argparse
from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication

from src.data.database_manager import DatabaseManager
from src.data.schema_manager import SchemaManager
from src.data.seed_data import seed_dev_data
from src.ui.main_window import MainWindow


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument('--db-path', default='data/budgeting_app.db')
    p.add_argument('--seed', action='store_true')
    return p.parse_args()


def main() -> int:
    args = parse_args()
    db = DatabaseManager(Path(args.db_path))
    conn = db.connect()
    SchemaManager(conn, Path('migrations')).run_migrations()
    if args.seed:
        seed_dev_data(conn)

    app = QApplication(sys.argv)
    win = MainWindow(conn)
    win.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
