from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ColumnScheme:
    def __init__(self, head: list[dict], measurements: list[dict]):
        self.head = ColumnSchemeSection(head)
        self.measurements = ColumnSchemeSection(measurements)

    @staticmethod
    def from_file(path: Path | str, template: str = '{}') -> ColumnScheme:
        if not isinstance(path, Path):
            path = Path(path)
        if not path.is_file():
            logger.info('Create new column scheme config file ' + str(path.absolute()))
            path.parent.mkdir(exist_ok=True)
            with open(path, 'w') as file:
                file.write(template)
        with open(path, 'r') as file:
            scheme = json.load(file)
            return ColumnScheme(scheme['head'], scheme['measurements'])


class ColumnSchemeSection:
    def __init__(self, data: list[dict]):
        self.data = data
        self.by_name = {}
        for entry in data:
            try:
                entry_name = entry.get('override_name', entry['name'])
            except KeyError as err:
                raise KeyError(f'Property `name` missing in column scheme for object `{entry}`') from err
            if entry_name in self.by_name.keys():
                raise KeyError(f'Duplicate column name/override_name `{entry_name}`')
            self.by_name[entry_name] = entry

    def __getitem__(self, key) -> str | dict:
        return self.data[key]

    def __len__(self) -> int:
        return len(self.data)
