from __future__ import annotations

from datetime import datetime, timezone, date
import sqlite3


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def seed_dev_data(conn: sqlite3.Connection) -> None:
    now = _now()
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO app_settings(key, value) VALUES('current_balance', '2500.00')"
        )
        conn.execute(
            "INSERT INTO accounts(name, kind, is_active, created_utc) VALUES(?, ?, 1, ?)",
            ('Checking', 'checking', now),
        )
        account_id = conn.execute('SELECT id FROM accounts WHERE name = ?', ('Checking',)).fetchone()['id']

        categories = [
            ('Mortgage', 'expense', 1, 1), ('HOA', 'expense', 2, 1), ('Phone', 'expense', 3, 1),
            ('Internet', 'expense', 4, 1), ('Electricity', 'expense', 5, 1), ('Gas', 'expense', 6, 1),
            ('Groceries', 'expense', 7, 1), ('Student Loan', 'expense', 8, 1), ('Car Insurance', 'expense', 9, 1),
            ('Tabs', 'expense', 10, 0), ('Toll Payoff', 'expense', 11, 0), ('Subscriptions', 'expense', 12, 0),
        ]
        for name, t, rank, req in categories:
            conn.execute(
                'INSERT OR IGNORE INTO categories(name, type, priority_rank, is_required, created_utc) VALUES(?, ?, ?, ?, ?)',
                (name, t, rank, req, now),
            )

        recurring = [
            ('Mortgage', 1200, 'outflow', 'monthly', 1, 10, None),
            ('Phone', 85, 'outflow', 'monthly', 1, 6, None),
            ('Groceries', 110, 'outflow', 'weekly', 1, None, 3),
            ('Gas', 60, 'outflow', 'weekly', 1, None, 0),
            ('Internet', 75, 'outflow', 'monthly', 1, 12, None),
            ('Electricity', 140, 'outflow', 'monthly', 1, 15, None),
            ('Student Loan', 260, 'outflow', 'monthly', 1, 22, None),
            ('Car Insurance', 145, 'outflow', 'monthly', 1, 18, None),
            ('HOA', 95, 'outflow', 'monthly', 1, 5, None),
            ('Tabs', 40, 'outflow', 'weekly', 1, None, 5),
            ('Toll Payoff', 35, 'outflow', 'weekly', 1, None, 2),
            ('Subscriptions', 25, 'outflow', 'monthly', 1, 2, None),
        ]
        for name, amt, direction, cadence, interval, dom, dow in recurring:
            category_id = conn.execute('SELECT id FROM categories WHERE name = ?', (name,)).fetchone()['id']
            conn.execute(
                '''INSERT INTO recurring_templates(
                    account_id, category_id, name, base_amount, direction, cadence_type, cadence_interval,
                    day_of_month, day_of_week, start_date, end_date, is_required, is_active, notes, created_utc, updated_utc
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, 1, 1, '', ?, ?)''',
                (
                    account_id,
                    category_id,
                    name,
                    amt,
                    direction,
                    cadence,
                    interval,
                    dom,
                    dow,
                    date.today().replace(day=1).isoformat(),
                    now,
                    now,
                ),
            )

        conn.execute(
            '''INSERT INTO income_rules(name, start_date, end_date, cadence_type, cadence_interval, base_amount, notes, is_active, created_utc, updated_utc)
               VALUES(?, ?, NULL, 'weekly', 2, ?, '', 1, ?, ?)''',
            ('Paycheck', date.today().isoformat(), 1850, now, now),
        )
