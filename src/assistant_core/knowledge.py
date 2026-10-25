"""Load and search assistant knowledge sources."""

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from assistant_core.errors import DataError


def _require_non_empty_string(
    value: Any,
    field: str,
    source: str,
) -> str:
    """Validate that a field is a non-empty string."""

    if not isinstance(value, str) or not value.strip():
        raise DataError(f"Invalid {source}: field '{field}' must be a non-empty string.")

    return value.strip()


@dataclass(frozen=True)
class Office:
    name: str
    room: str
    hours: str


class OfficeDirectory:
    def __init__(self, offices: dict[str, Office]):
        self._offices = offices

    @classmethod
    def from_csv(cls, path: Path) -> "OfficeDirectory":
        """Load office data from CSV."""

        try:
            with path.open(
                encoding="utf-8",
                newline="",
            ) as file:
                rows = list(csv.DictReader(file))

        except FileNotFoundError as exc:
            raise DataError(f"Office file not found: {path}") from exc

        offices = {
            row["name"].lower(): Office(
                name=row["name"],
                room=row["room"],
                hours=row["hours"],
            )
            for row in rows
        }

        return cls(offices)

    @property
    def names(self) -> set[str]:
        return set(self._offices)

    def find(self, text: str) -> Office | None:
        """Find an office mentioned in the text."""

        text = text.lower()

        return next(
            (office for name, office in self._offices.items() if name in text),
            None,
        )


@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    text: str


class Handbook:
    REQUIRED_FIELDS = frozenset(("id", "title", "text"))
    def __init__(self, rules: list[Rule]):
        self._rules = rules
        

    @classmethod
    def from_json(cls, path: Path) -> "Handbook":
        """Load handbook rules from JSON."""

        try:
            with path.open(encoding="utf-8") as file:
                data = json.load(file)

        except FileNotFoundError as exc:
            raise DataError(f"Handbook file not found: {path}") from exc

        except json.JSONDecodeError as exc:
            raise DataError(f"Invalid handbook JSON: {path}") from exc

        if not isinstance(data, list):
            raise DataError(f"Invalid handbook JSON: expected a list: {path}")

        if not data:
            raise DataError(f"Invalid handbook JSON: no rules found: {path}")

        rules: list[Rule] = []
        seen_ids: set[str] = set()

        for index, item in enumerate(data):
            if not isinstance(item, dict):
                raise DataError(f"Invalid handbook JSON at index {index}: expected an object.")

            missing_fields = cls.REQUIRED_FIELDS - item.keys()

            if missing_fields:
                raise DataError(f"Invalid handbook JSON at index {index}: missing fields {sorted(missing_fields)}.")

            rule_id = _require_non_empty_string(
                item["id"],
                "id",
                f"handbook JSON at index {index}",
            )

            title = _require_non_empty_string(
                item["title"],
                "title",
                f"handbook JSON at index {index}",
            )

            text = _require_non_empty_string(
                item["text"],
                "text",
                f"handbook JSON at index {index}",
            )

            if rule_id in seen_ids:
                raise DataError(f"Duplicate handbook rule id: '{rule_id}'.")

            seen_ids.add(rule_id)

            rules.append(
                Rule(
                    id=rule_id,
                    title=title,
                    text=text,
                )
            )

        return cls(rules)

    def search(self, query: str) -> Rule | None:
        query = query.lower()

        return next(
            (rule for rule in self._rules if query in rule.title.lower() or query in rule.text.lower()),
            None,
        )
