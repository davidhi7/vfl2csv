# vfl2csv

Two Utilities developed for TU Dresden Chair of Forest Growth and Woody Biomass Production.

1. Command line utility for converting outputs from the proprietary Versuchsflächendatenbanksystem into CSV files
2. GUI application based on `PySide6` and Qt that creates Excel forms for uncomplicated measurement acquisition

## Dependencies

* Python 3 and pip
* `pandas`
* `OpenPyXL`
* `PySide6`
* `PyInstaller` (for building)

```bash
python3 -m pip install -r requirements.txt
```

## Launch

### `vfl2csv`: command line utility for converting into CSV files

```bash
vfl2csv$ python3 -m vfl2csv path/to/input path/to/output
```

### `vfl2csv_forms`: GUI application for Excel form generation

```bash
vfl2csv$ python3 -m vfl2csv_forms
```

## Configuration

### common configuration

`config/columns.json`:
JSON-file describing the column scheme of CSV files that are created with or used by programs from this repository.
The general format is:

```json
{
  "head": [
    <column1>,
    <column2>,
    ...
  ],
  "measurements": [
    <column3>,
    <column4>,
    ...
  ]
}
```

where `<column1>` and `<column2>` are placeholders for head columns that list tree identifications and metadata.
`<column3>` and `<column4>` represent measurement columns.
Incrementally, new measurements are recorded and all individual measurement columns must be added in the defined order
to the CSV file.
Each column is described by a JSON object containing the following required and optional key-value-pairs:

| Key name            |                 expected value                  | required | comment                                                                                                                                                                                                                                                                                                |
|---------------------|:-----------------------------------------------:|:--------:|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `overwrite_name`    |                      `str`                      |    x     | Name of the column, appears in the CSV files and forms as header. Starts with `override`, because it overrides the initial name in the input files for `vfl2csv`.                                                                                                                                      |
| `type`              | `string`, `{u,}int{8,16,32,64}`, `float{32,64}` |    x     | Datatype that best fits the values in the columns.                                                                                                                                                                                                                                                     |
| `form_include`      |                `true` or `false`                |          | Whether this column should be part of forms                                                                                                                                                                                                                                                            |
| `new_columns_count` |                      `int`                      |          | If `form_include == true`: How many input columns should be inserted into forms to allow multiple measurements per tree. For example, often two measurements are used for estimating the tree's real diameter. If `> 1`, another column will calculate the mean values of all measurements for a tree. |
| `add_difference`    |                `true` or `false`                |          | If `true`, a dedicated column will be inserted into forms calculating the difference between the new and last older measurements.                                                                                                                                                                      |                                                                                                                                                                                                                                                

All head columns must only occur once in the CSV file.
Measurement columns can occur multiple times but must always be in the right order, without any columns missing.

### vfl2csv

`config/config_vfl2csv.ini`

### vfl2csv_forms

`config/config_forms.ini`
