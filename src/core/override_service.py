from __future__ import annotations

from copy import deepcopy


class OverrideService:
    def apply_overrides(self, projected_items: list[dict], overrides: list[dict]) -> list[dict]:
        override_map = {
            (o['source_kind'], o['source_id'], o['effective_date']): o for o in overrides
        }
        updated: list[dict] = []
        for item in projected_items:
            key = (item['source_kind'], item['source_id'], item['date'])
            override = override_map.get(key)
            if not override:
                updated.append(item)
                continue

            if override['is_skip']:
                continue

            row = deepcopy(item)
            if override['replacement_date']:
                row['date'] = override['replacement_date']
            if override['replacement_amount'] is not None:
                row['amount'] = float(override['replacement_amount'])
            row['is_overridden'] = 1
            row['override_kind'] = override['override_kind']
            updated.append(row)

        return updated
