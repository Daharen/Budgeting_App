from datetime import date
import sqlite3

from src.core.override_service import OverrideService
from src.core.recurrence_service import RecurrenceRule, RecurrenceService
from src.core.timeline_service import TimelineService
from src.data.schema_manager import SchemaManager


def make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    SchemaManager(conn, 'migrations').run_migrations()
    return conn


def test_weekly_recurrence_expansion_is_deterministic():
    svc = RecurrenceService()
    rule = RecurrenceRule(
        cadence_type='weekly',
        cadence_interval=1,
        start_date=date(2026, 1, 1),
        end_date=None,
        day_of_week=3,
    )
    out = svc.expand(rule, date(2026, 1, 1), date(2026, 1, 31))
    assert [d.isoformat() for d in out] == ['2026-01-01', '2026-01-08', '2026-01-15', '2026-01-22', '2026-01-29']


def test_override_skip_and_amount_change():
    projected = [
        {'source_kind': 'recurring_template', 'source_id': 1, 'date': '2026-01-10', 'amount': 100, 'direction': 'outflow'},
        {'source_kind': 'recurring_template', 'source_id': 1, 'date': '2026-02-10', 'amount': 100, 'direction': 'outflow'},
    ]
    overrides = [
        {'source_kind': 'recurring_template', 'source_id': 1, 'effective_date': '2026-01-10', 'override_kind': 'skip', 'replacement_date': None, 'replacement_amount': None, 'is_skip': 1},
        {'source_kind': 'recurring_template', 'source_id': 1, 'effective_date': '2026-02-10', 'override_kind': 'reduce', 'replacement_date': None, 'replacement_amount': 80, 'is_skip': 0},
    ]
    out = OverrideService().apply_overrides(projected, overrides)
    assert len(out) == 1
    assert out[0]['amount'] == 80


def test_timeline_running_balance_and_negative_detection():
    conn = make_conn()
    now = '2026-01-01T00:00:00+00:00'
    with conn:
        conn.execute("INSERT INTO app_settings(key, value) VALUES('current_balance', '100')")
        conn.execute("INSERT INTO accounts(name, kind, is_active, created_utc) VALUES('Checking', 'checking', 1, ?)", (now,))
        conn.execute("INSERT INTO categories(name, type, priority_rank, is_required, created_utc) VALUES('Rent', 'expense', 1, 1, ?)", (now,))
        conn.execute(
            """INSERT INTO recurring_templates(account_id, category_id, name, base_amount, direction, cadence_type, cadence_interval,
                day_of_month, day_of_week, start_date, end_date, is_required, is_active, notes, created_utc, updated_utc)
                VALUES(1, 1, 'Rent', 200, 'outflow', 'monthly', 1, 2, NULL, '2026-01-01', NULL, 1, 1, '', ?, ?)""",
            (now, now),
        )
    rows, summary = TimelineService(conn).generate(date(2026, 1, 1), days_forward=30)
    assert rows[0]['running_balance'] == -100
    assert summary.first_negative_date == '2026-01-02'
