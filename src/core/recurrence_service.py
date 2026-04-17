from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from calendar import monthrange


@dataclass(frozen=True)
class RecurrenceRule:
    cadence_type: str
    cadence_interval: int
    start_date: date
    end_date: date | None
    day_of_month: int | None = None
    day_of_week: int | None = None


class RecurrenceService:
    def expand(self, rule: RecurrenceRule, horizon_start: date, horizon_end: date) -> list[date]:
        if horizon_end < horizon_start:
            return []
        if rule.cadence_type == 'daily':
            return self._expand_daily(rule, horizon_start, horizon_end)
        if rule.cadence_type == 'weekly':
            return self._expand_weekly(rule, horizon_start, horizon_end)
        if rule.cadence_type == 'monthly':
            return self._expand_monthly(rule, horizon_start, horizon_end)
        raise ValueError(f'Unsupported cadence_type: {rule.cadence_type}')

    def _in_range(self, candidate: date, rule: RecurrenceRule, start: date, end: date) -> bool:
        if candidate < start or candidate > end:
            return False
        if candidate < rule.start_date:
            return False
        if rule.end_date and candidate > rule.end_date:
            return False
        return True

    def _expand_daily(self, rule: RecurrenceRule, start: date, end: date) -> list[date]:
        step = timedelta(days=max(rule.cadence_interval, 1))
        d = rule.start_date
        out: list[date] = []
        while d <= end:
            if self._in_range(d, rule, start, end):
                out.append(d)
            d += step
        return out

    def _expand_weekly(self, rule: RecurrenceRule, start: date, end: date) -> list[date]:
        target_dow = 0 if rule.day_of_week is None else rule.day_of_week
        interval = max(rule.cadence_interval, 1)
        seed = rule.start_date
        while seed.weekday() != target_dow:
            seed += timedelta(days=1)

        out: list[date] = []
        d = seed
        while d <= end:
            weeks_since_seed = (d - seed).days // 7
            if weeks_since_seed % interval == 0 and self._in_range(d, rule, start, end):
                out.append(d)
            d += timedelta(days=7)
        return out

    def _expand_monthly(self, rule: RecurrenceRule, start: date, end: date) -> list[date]:
        dom = rule.day_of_month or rule.start_date.day
        interval = max(rule.cadence_interval, 1)
        y, m = rule.start_date.year, rule.start_date.month
        out: list[date] = []

        index = 0
        while date(y, m, 1) <= end:
            if index % interval == 0:
                last_day = monthrange(y, m)[1]
                candidate = date(y, m, min(dom, last_day))
                if self._in_range(candidate, rule, start, end):
                    out.append(candidate)
            index += 1
            m += 1
            if m > 12:
                y += 1
                m = 1
        return out
