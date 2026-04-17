from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import sqlite3

from src.core.override_service import OverrideService
from src.core.recurrence_service import RecurrenceRule, RecurrenceService


@dataclass
class TimelineSummary:
    current_balance: float
    first_negative_date: str | None
    lowest_projected_balance: float
    lowest_projected_date: str | None
    net_30: float
    net_60: float
    net_90: float


class TimelineService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.recurrence = RecurrenceService()
        self.overrides = OverrideService()

    def generate(self, as_of: date, days_forward: int = 90, include_history: bool = False) -> tuple[list[dict], TimelineSummary]:
        start = as_of if not include_history else as_of - timedelta(days=3650)
        end = as_of + timedelta(days=days_forward)

        projected = self._expand_projected(start, end)
        actual = self._actual_rows(start if include_history else as_of - timedelta(days=3650), end)
        merged = actual + projected

        merged.sort(key=lambda r: (r['date'], 0 if r['kind'] == 'actual' else 1, r.get('source_kind', ''), r.get('source_id', 0), r.get('id', 0)))

        running = self._current_balance_before(as_of)
        first_negative = None
        low_balance = running
        low_date = None
        net_30 = 0.0
        net_60 = 0.0
        net_90 = 0.0

        for row in merged:
            signed = row['amount'] if row['direction'] == 'inflow' else -row['amount']
            running += signed
            row['running_balance'] = round(running, 2)
            row['is_negative'] = 1 if running < 0 else 0
            if row['date'] >= as_of.isoformat() and first_negative is None and running < 0:
                first_negative = row['date']
            if row['date'] >= as_of.isoformat() and running < low_balance:
                low_balance = running
                low_date = row['date']

            d = date.fromisoformat(row['date'])
            if d >= as_of and d <= as_of + timedelta(days=30):
                net_30 += signed
            if d >= as_of and d <= as_of + timedelta(days=60):
                net_60 += signed
            if d >= as_of and d <= as_of + timedelta(days=90):
                net_90 += signed

        summary = TimelineSummary(
            current_balance=round(self._current_balance_before(as_of), 2),
            first_negative_date=first_negative,
            lowest_projected_balance=round(low_balance, 2),
            lowest_projected_date=low_date,
            net_30=round(net_30, 2),
            net_60=round(net_60, 2),
            net_90=round(net_90, 2),
        )
        return merged, summary

    def _current_balance_before(self, as_of: date) -> float:
        base = self.conn.execute("SELECT value FROM app_settings WHERE key='current_balance'").fetchone()
        running = float(base['value']) if base else 0.0
        rows = self.conn.execute(
            '''SELECT amount, direction FROM actual_transactions WHERE transaction_date < ? ORDER BY transaction_date ASC, id ASC''',
            (as_of.isoformat(),),
        ).fetchall()
        for r in rows:
            running += r['amount'] if r['direction'] == 'inflow' else -r['amount']
        return running

    def _actual_rows(self, start: date, end: date) -> list[dict]:
        rows = self.conn.execute(
            '''
            SELECT a.id, a.transaction_date AS date, a.description, a.amount, a.direction, a.status,
                   c.name AS category
            FROM actual_transactions a
            LEFT JOIN categories c ON c.id = a.category_id
            WHERE a.transaction_date BETWEEN ? AND ?
            ''',
            (start.isoformat(), end.isoformat()),
        ).fetchall()
        return [
            {
                'id': row['id'],
                'date': row['date'],
                'kind': 'actual',
                'category': row['category'] or 'Uncategorized',
                'description': row['description'],
                'amount': float(row['amount']),
                'direction': row['direction'],
                'status': row['status'],
                'required': 0,
            }
            for row in rows
        ]

    def _expand_projected(self, start: date, end: date) -> list[dict]:
        items: list[dict] = []

        templates = self.conn.execute(
            '''SELECT rt.*, c.name AS category_name
               FROM recurring_templates rt
               LEFT JOIN categories c ON c.id = rt.category_id
               WHERE rt.is_active = 1'''
        ).fetchall()

        for t in templates:
            rule = RecurrenceRule(
                cadence_type=t['cadence_type'],
                cadence_interval=t['cadence_interval'],
                start_date=date.fromisoformat(t['start_date']),
                end_date=date.fromisoformat(t['end_date']) if t['end_date'] else None,
                day_of_month=t['day_of_month'],
                day_of_week=t['day_of_week'],
            )
            for d in self.recurrence.expand(rule, start, end):
                items.append(
                    {
                        'date': d.isoformat(),
                        'kind': 'projected',
                        'category': t['category_name'] or 'Uncategorized',
                        'description': t['name'],
                        'amount': float(t['base_amount']),
                        'direction': t['direction'],
                        'status': 'projected',
                        'required': t['is_required'],
                        'source_kind': 'recurring_template',
                        'source_id': t['id'],
                    }
                )

        incomes = self.conn.execute('SELECT * FROM income_rules WHERE is_active = 1').fetchall()
        for i in incomes:
            rule = RecurrenceRule(
                cadence_type=i['cadence_type'],
                cadence_interval=i['cadence_interval'],
                start_date=date.fromisoformat(i['start_date']),
                end_date=date.fromisoformat(i['end_date']) if i['end_date'] else None,
            )
            for d in self.recurrence.expand(rule, start, end):
                items.append(
                    {
                        'date': d.isoformat(),
                        'kind': 'projected',
                        'category': 'Income',
                        'description': i['name'],
                        'amount': float(i['base_amount']),
                        'direction': 'inflow',
                        'status': 'projected',
                        'required': 1,
                        'source_kind': 'income_rule',
                        'source_id': i['id'],
                    }
                )

        overrides = self.conn.execute('SELECT * FROM timeline_overrides').fetchall()
        override_rows = [dict(row) for row in overrides]
        return self.overrides.apply_overrides(items, override_rows)
