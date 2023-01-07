import json
from pathlib import Path


class ColumnLayout:
    def __init__(self, path: Path):
        with open(path, 'r') as file:
            self.layout = json.load(file)
            self.head = ColumnLayoutSection(self.layout['head'])
            self.measurements = ColumnLayoutSection(self.layout['measurements'])


class ColumnLayoutSection:
    def __init__(self, data: list[dict]):
        self.data = data
        self.by_name = {entry['override_name']: entry for entry in data}

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        return len(self.data)
