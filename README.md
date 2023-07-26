# vfl2csv

Two utilities developed for TU Dresden Chair of Forest Growth and Woody Biomass Production.

1. `vfl2csv`: CLI and GUI for converting outputs from the proprietary Versuchsflächendatenbanksystem into CSV files
2. `vfl2csv_forms`: GUI application that creates Excel forms for uncomplicated measurement acquisition from CSV files
   created by `vfl2csv`

Both components are part of the unified GUI `vfl2csv_gui`.

## Dependencies

* Recent Python 3
* `pandas`
* `OpenPyXL`
* `PySide6`

```bash
$ python -m pip install -r requirements.txt
```

## Launch

```bash
$ python -m vfl2csv_gui
```

## Configuration

### common configuration

`config/columns.json`:
JSON-file describing the column scheme of CSV files that are created with or used by programs from this repository.
The general format is:

```json
{
  "head": [
    {
    },
    {
    }
  ],
  "measurements": [
    {
    },
    {
    }
  ]
}
```

The empty objects in `head` are placeholders for head columns that list tree identifications and metadata.
The empty objects in `mneasurements` are placeholders representing measurement columns.
Incrementally, new measurements are recorded and all individual measurement columns must be added in the defined order
to the CSV file.
Each column is described by a JSON object containing the following required and optional key-value-pairs:

| Key name                                     |                 expected value                  | required | comment                                                                                                                                                                                                                                                                                                |
|----------------------------------------------|:-----------------------------------------------:|:--------:|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `name`                                       |                      `str`                      |    x     | Name of the column, must be identical to the name of the corresponding column of the vfldb data excerpt                                                                                                                                                                                                |                                                                                                                                                                                                
| `override_name`                              |                      `str`                      |          | Override `name` in the CSV files and form header. **All `override_name` values, or if not present, `name` values must be unique.**                                                                                                                                                                     |
| `display_name`                               |                      `str`                      |          | Name used in forms. If provided, this setting overrides `override_name` exclusively in forms.                                                                                                                                                                                                          |
| `type`                                       | `string`, `{u,}int{8,16,32,64}`, `float{32,64}` |    x     | Datatype that best fits the values in the columns.                                                                                                                                                                                                                                                     |
| `form_include`                               |                `true` or `false`                |          | Whether this column should be part of forms                                                                                                                                                                                                                                                            |
| `new_columns_count` (only in `measurements`) |                      `int`                      |          | If `form_include == true`: How many input columns should be inserted into forms to allow multiple measurements per tree. For example, often two measurements are used for estimating the tree's real diameter. If `> 1`, another column will calculate the mean values of all measurements for a tree. |
| `add_difference` (only in `measurements`)    |                `true` or `false`                |          | If `true`, a dedicated column will be inserted into forms calculating the difference between the new and last older measurements.                                                                                                                                                                      |
| `optional` (only in `measurements`)          |                `true` or `false`                |          | If `true`, this column does not have to appear in every measurement. Must be set to `false` if `form_include` is `true`.                                                                                                                                                                               | 

All head columns must only occur once in the CSV file.
Measurement columns can occur multiple times but must always be in the right order, without any columns missing.

### vfl2csv

`config/config_vfl2csv.ini`

### vfl2csv_forms

`config/config_forms.ini`

## History

### 1.2.5

* More testing
* Add `display_name` property for all columns to configure formula column names

### 1.2.4

* Add documentation

### 1.2.3

* Fix bug with 1.2.2 form creation from vfl2csv GUI
* Code style improvements

### 1.2.2 2023-06-13

* Allow to create form directly from vfl2csv GUI
* Fixed error handling

### 1.2.1 2023-05-03

* Increase threshold for measurement year decrementation to 07-01 instead of 06-01
