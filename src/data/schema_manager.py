from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SchemaManager:
    def __init__(self, conn: sqlite3.Connection, migrations_dir: str | Path):
        self.conn = conn
        self.migrations_dir = Path(migrations_dir)

    def run_migrations(self) -> None:
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY, applied_utc TEXT NOT NULL)'
        )
        applied = {
            row['name']
            for row in self.conn.execute('SELECT name FROM schema_migrations').fetchall()
        }

        for migration in sorted(self.migrations_dir.glob('*.sql')):
            if migration.name in applied:
                continue
            sql = migration.read_text(encoding='utf-8')
            with self.conn:
                self.conn.executescript(sql)
                self.conn.execute(
                    'INSERT INTO schema_migrations(name, applied_utc) VALUES(?, ?)',
                    (migration.name, utc_now_iso()),
                )
