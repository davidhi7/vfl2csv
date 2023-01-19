from __future__ import annotations

import json
from pathlib import Path


class ColumnScheme:
    def __init__(self, head: list[dict], measurements: list[dict]):
        self.head = ColumnSchemeSection(head)
        self.measurements = ColumnSchemeSection(measurements)

    @staticmethod
    def from_file(path: Path) -> ColumnScheme:
        with open(path, 'r') as file:
            scheme = json.load(file)
            return ColumnScheme(scheme['head'], scheme['measurements'])


class ColumnSchemeSection:
    def __init__(self, data: list[dict]):
        self.data = data
        self.by_name = {entry['override_name']: entry for entry in data}

    def __getitem__(self, key) -> str | dict:
        return self.data[key]

    def __len__(self) -> int:
        return len(self.data)
