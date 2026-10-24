"""Load and search assistant knowledge sources."""

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from assistant_core.errors import DataError


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
            raise DataError(
                f"Office file not found: {path}"
            ) from exc

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
            (
                office
                for name, office in self._offices.items()
                if name in text
            ),
            None,
        )


@dataclass(frozen=True)
class Rule:
    title: str
    tittle: str
    text: str


class Handbook:
    def __init__(self, rules: list[Rule]):
        self._rules = rules

    @classmethod
    def from_json(cls, path: Path) -> "Handbook":
        """Load handbook rules from JSON."""

        try:
            with path.open(encoding="utf-8") as file:
                data = json.load(file)

        except FileNotFoundError as exc:
            raise DataError(
                f"Handbook file not found: {path}"
            ) from exc

        except json.JSONDecodeError as exc:
            raise DataError(
                f"Invalid handbook JSON: {path}"
            ) from exc

        rules = [
            Rule(
                id=item["id"],
                title=item["title"],
                text=item["text"],
            )
            for item in data
        ]

        return cls(rules)

    def search(self, query: str) -> Rule | None:
        query = query.lower()

        return next(
            (
                rule
                for rule in self._rules
                if query in rule.title.lower()
                or query in rule.content.lower()
            ),
            None,
        )