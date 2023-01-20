# Benchmark results
## System
* Archlinux
* Python 3.10
* OenPyXL 3.0.10
* pandas 1.5.2
* PyInstaller 5.7.0
* Nuitka 1.3.8

## Configuration

1. `Unprocessed Python`: unprocessed python source code
2. `PyInstaller`: `python -m PyInstaller --add-data config:config vfl2csv_forms_benchmark/__main__.py`
3. `Nuitka`: `python -m nuitka --standalone --follow-imports --include-data-files=config/config_forms.ini=config/config_forms.ini --include-data-files=config/columns.json=config/columns.json vfl2csv_forms_benchmark/__main__.py`

* Iterations: 100
* Input trial sites: 23

## Results
all times are provided in seconds.

| Metric  | Unprocessed Python | PyInstaller | Nuitka |
|---------|--------------------|-------------|--------|
| count   | 100                | 100         | 100    |
| mean    | 3.629              | 3.767       | 3.523  |
| std     | 0.040              | 0.059       | 0.048  |
| min     | 3.559              | 3.669       | 3.439  |
| 25,00 % | 3.606              | 3.726       | 3.489  |
| 50,00 % | 3.620              | 3.752       | 3.515  |
| 75,00 % | 3.643              | 3.800       | 3.548  |
| max     | 3.816              | 3.989       | 3.676  |
