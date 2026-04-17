PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS accounts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  kind TEXT NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  type TEXT NOT NULL,
  priority_rank INTEGER NOT NULL DEFAULT 100,
  is_required INTEGER NOT NULL DEFAULT 0,
  created_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS actual_transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_id INTEGER NOT NULL,
  category_id INTEGER,
  transaction_date TEXT NOT NULL,
  description TEXT NOT NULL,
  amount REAL NOT NULL,
  direction TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'posted',
  notes TEXT,
  created_utc TEXT NOT NULL,
  updated_utc TEXT NOT NULL,
  FOREIGN KEY(account_id) REFERENCES accounts(id),
  FOREIGN KEY(category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS recurring_templates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_id INTEGER NOT NULL,
  category_id INTEGER,
  name TEXT NOT NULL,
  base_amount REAL NOT NULL,
  direction TEXT NOT NULL,
  cadence_type TEXT NOT NULL,
  cadence_interval INTEGER NOT NULL DEFAULT 1,
  day_of_month INTEGER,
  day_of_week INTEGER,
  start_date TEXT NOT NULL,
  end_date TEXT,
  is_required INTEGER NOT NULL DEFAULT 1,
  is_active INTEGER NOT NULL DEFAULT 1,
  notes TEXT,
  created_utc TEXT NOT NULL,
  updated_utc TEXT NOT NULL,
  FOREIGN KEY(account_id) REFERENCES accounts(id),
  FOREIGN KEY(category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS timeline_overrides (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_kind TEXT NOT NULL,
  source_id INTEGER NOT NULL,
  effective_date TEXT NOT NULL,
  override_kind TEXT NOT NULL,
  replacement_date TEXT,
  replacement_amount REAL,
  is_skip INTEGER NOT NULL DEFAULT 0,
  notes TEXT,
  created_utc TEXT NOT NULL,
  updated_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS income_rules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  start_date TEXT NOT NULL,
  end_date TEXT,
  cadence_type TEXT NOT NULL,
  cadence_interval INTEGER NOT NULL DEFAULT 1,
  base_amount REAL NOT NULL,
  notes TEXT,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_utc TEXT NOT NULL,
  updated_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS app_settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
