# Budgeting App Baseline (Qt + SQLite)

Local deterministic cash timeline planner focused on survival/recovery forecasting.

## Features (v1)
- SQLite schema + migration support
- Deterministic timeline generation from source tables:
  - actual ledger entries
  - recurring templates
  - income rules
  - explicit timeline overrides
  - app settings (current balance)
- Planned vs actual kept separate
- Override semantics: skip, reschedule, amount replacement
- Qt desktop tabs:
  - Timeline
  - Recurring (including income rules)
  - Actuals
  - Overrides
  - Summary
- Dev seed data for realistic obligations

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.app.main --seed
```

## Tests
```bash
pytest -q
```
